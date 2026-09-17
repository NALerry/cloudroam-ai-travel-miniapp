<template>
  <view class="my-posts-page">
    <!-- 导航栏 -->
    <view class="navbar">
      <image src="/static/icons/general/back.png" class="nav-icon" @tap="goBack"></image>
      <text class="nav-title">我的投稿</text>
      <view class="nav-right">
        <text class="nav-count">共{{ posts.length }}篇</text>
      </view>
    </view>

    <!-- 内容区域 -->
    <scroll-view class="content-scroll" scroll-y :style="{height: scrollHeight + 'px'}" @refresherrefresh="onRefresh" refresher-enabled>
      <!-- 筛选标签 -->
      <view class="filter-tabs">
        <view 
          class="tab-item" 
          :class="{active: currentTab === 'all'}"
          @tap="switchTab('all')"
        >
          <text>全部</text>
        </view>
        <view 
          class="tab-item" 
          :class="{active: currentTab === 'published'}"
          @tap="switchTab('published')"
        >
          <text>已发布</text>
        </view>
        <view 
          class="tab-item" 
          :class="{active: currentTab === 'draft'}"
          @tap="switchTab('draft')"
        >
          <text>草稿箱</text>
        </view>
      </view>

      <!-- 帖子列表 -->
      <view class="posts-list">
        <view 
          class="post-item" 
          v-for="post in filteredPosts" 
          :key="post.id"
          @tap="viewPostDetail(post)"
        >
          <view class="post-header">
            <text class="post-title">{{ post.title }}</text>
            <view class="post-status" :class="post.status">
              <text>{{ post.status === 'published' ? '已发布' : '草稿' }}</text>
            </view>
          </view>
          
          <text class="post-content">{{ post.content }}</text>
          
          <view class="post-images" v-if="post.imagesList && post.imagesList.length > 0">
            <image 
              v-for="(img, index) in post.imagesList.slice(0, 3)" 
              :key="index"
              class="post-image"
              :src="getFullImageUrl(img)"
              mode="aspectFill"
            ></image>
          </view>
          
          <view class="post-footer">
            <text class="post-time">{{ post.createTime }}</text>
            <view class="post-stats">
              <view class="stat">
                <image src="/static/icons/general/like.png" class="stat-icon"></image>
                <text>{{ post.likeCount || 0 }}</text>
              </view>
              <view class="stat">
                <image src="/static/icons/general/comment.png" class="stat-icon"></image>
                <text>{{ post.commentCount || 0 }}</text>
              </view>
            </view>
          </view>
          
          <view class="post-actions">
            <view class="action-btn edit" @tap.stop="editPost(post)">
              <image src="/static/icons/general/edit.png" class="action-icon"></image>
              <text>编辑</text>
            </view>
            <view class="action-btn delete" @tap.stop="deletePost(post)">
              <image src="/static/icons/general/delete.png" class="action-icon"></image>
              <text>删除</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <view class="empty-state" v-if="filteredPosts.length === 0 && !isLoading">
        <image src="/static/icons/general/post.png" class="empty-icon"></image>
        <text class="empty-text">暂无投稿内容</text>
        <text class="empty-desc">快去分享你的旅行故事吧～</text>
        <view class="empty-btn" @tap="createNewPost">
          <text>立即投稿</text>
        </view>
      </view>
    </scroll-view>

    <!-- 编辑对话框 -->
    <view class="dialog-mask" v-if="showEditDialog" @tap="closeEditDialog">
      <view class="dialog-content" @tap.stop>
        <view class="dialog-header">
          <text class="dialog-title">编辑帖子</text>
          <text class="dialog-close" @tap="closeEditDialog">✕</text>
        </view>
        <scroll-view class="dialog-body" scroll-y>
          <view class="form-group">
            <text class="form-label">标题</text>
            <input 
              class="form-input" 
              v-model="editForm.title" 
              placeholder="请输入标题"
              maxlength="50"
            />
          </view>
          <view class="form-group">
            <text class="form-label">内容</text>
            <textarea 
              class="form-textarea" 
              v-model="editForm.content" 
              placeholder="请输入内容"
              maxlength="1000"
              auto-height
            ></textarea>
          </view>
          <view class="form-group">
            <text class="form-label">图片（最多9张）</text>
            <view class="image-list">
              <view 
                class="image-item" 
                v-for="(img, index) in editForm.images" 
                :key="index"
              >
                <image :src="getFullImageUrl(img)" class="upload-image" mode="aspectFill"></image>
                <view class="image-delete" @tap.stop="removeImage(index)">✕</view>
              </view>
              <view 
                class="image-add" 
                v-if="editForm.images.length < 9"
                @tap="chooseImage"
              >
                <text class="add-icon">+</text>
              </view>
            </view>
          </view>
        </scroll-view>
        <view class="dialog-footer">
          <button class="dialog-btn cancel" @tap="closeEditDialog">取消</button>
          <button class="dialog-btn draft" @tap="saveAsDraft" v-if="editForm.status === 'draft'">保存草稿</button>
          <button class="dialog-btn confirm" @tap="submitEdit">{{ editForm.status === 'draft' ? '发布' : '保存修改' }}</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      currentTab: 'all',
      scrollHeight: 0,
      posts: [],
      isLoading: false,
      userId: 1,
      showEditDialog: false,
      editForm: {
        id: null,
        title: '',
        content: '',
        images: [],
        status: 'draft'
      },
      baseUrl: 'http://localhost:8080'
    }
  },
  computed: {
    filteredPosts() {
      if (this.currentTab === 'all') {
        return this.posts
      }
      return this.posts.filter(post => post.status === this.currentTab)
    }
  },
  onLoad() {
    this.calculateScrollHeight()
    this.getUserInfo()
    this.loadMyPosts()
  },
  onShow() {
    this.loadMyPosts()
  },
  onResize() {
    this.calculateScrollHeight()
  },
  onPullDownRefresh() {
    this.loadMyPosts()
  },
  methods: {
    getFullImageUrl(url) {
      if (!url) return ''
      if (url.startsWith('http://') || url.startsWith('https://')) {
        return url
      }
      return this.baseUrl + url
    },

    async getUserInfo() {
      try {
        const userInfo = uni.getStorageSync('userInfo')
        if (userInfo) {
          this.userId = userInfo.id
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
      }
    },

    calculateScrollHeight() {
      const systemInfo = uni.getSystemInfoSync()
      const windowHeight = systemInfo.windowHeight
      const statusBarHeight = systemInfo.statusBarHeight || 0
      const navigationBarHeight = 44
      this.scrollHeight = windowHeight - statusBarHeight - navigationBarHeight
    },
    
    async loadMyPosts() {
      if (this.isLoading) return
      
      this.isLoading = true
      try {
        const res = await uni.request({
          url: `${this.baseUrl}/api/posts/user/${this.userId}`,
          method: 'GET'
        })
        
        if (res.data.success) {
          this.posts = res.data.data.map(post => {
            if (post.imageUrls) {
              try {
                post.imagesList = JSON.parse(post.imageUrls)
              } catch (e) {
                post.imagesList = []
              }
            } else {
              post.imagesList = []
            }
            post.createTime = this.formatTime(post.createdAt)
            return post
          })
        } else {
          uni.showToast({ title: res.data.message || '加载失败', icon: 'none' })
        }
      } catch (error) {
        console.error('加载投稿失败:', error)
        uni.showToast({ title: '网络错误', icon: 'none' })
      } finally {
        this.isLoading = false
        uni.stopPullDownRefresh()
      }
    },
    
    onRefresh() {
      this.loadMyPosts()
    },
    
    goBack() {
      uni.navigateBack()
    },
    
    switchTab(tab) {
      this.currentTab = tab
    },
    
    viewPostDetail(post) {
      uni.navigateTo({
        url: `/pages/post-detail/post-detail?id=${post.id}`
      })
    },
    
    editPost(post) {
      this.editForm = {
        id: post.id,
        title: post.title,
        content: post.content,
        images: [...(post.imagesList || [])],
        status: post.status
      }
      this.showEditDialog = true
    },
    
    closeEditDialog() {
      this.showEditDialog = false
      this.editForm = {
        id: null,
        title: '',
        content: '',
        images: [],
        status: 'draft'
      }
    },
    
    chooseImage() {
      const maxCount = 9 - this.editForm.images.length
      uni.chooseImage({
        count: maxCount,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
        success: (res) => {
          this.editForm.images.push(...res.tempFilePaths)
        }
      })
    },
    
    removeImage(index) {
      this.editForm.images.splice(index, 1)
    },
    
    uploadImage(filePath) {
      console.log('上传图片到:', `${this.baseUrl}/api/upload/post`)
      console.log('文件路径:', filePath)
      
      return new Promise((resolve, reject) => {
        uni.uploadFile({
          url: `${this.baseUrl}/api/upload/post`,
          filePath: filePath,
          name: 'file',
          success: (res) => {
            console.log('上传响应状态码:', res.statusCode)
            console.log('上传响应数据:', res.data)
            try {
              const data = JSON.parse(res.data)
              if (data.success) {
                console.log('上传成功, URL:', data.url)
                resolve(data.url)
              } else {
                reject(new Error(data.message || '上传失败'))
              }
            } catch (e) {
              console.error('解析响应失败:', e)
              reject(new Error('解析响应失败'))
            }
          },
          fail: (err) => {
            console.error('上传请求失败:', err)
            reject(new Error('网络错误，上传失败'))
          }
        })
      })
    },
    
    async saveAsDraft() {
      if (!this.editForm.title.trim()) {
        uni.showToast({ title: '请输入标题', icon: 'none' })
        return
      }
      
      uni.showLoading({ title: '保存中...' })
      
      try {
        let imageUrls = []
        for (const img of this.editForm.images) {
          if (img.startsWith('http://tmp') || img.startsWith('file://') || img.startsWith('blob:')) {
            try {
              const uploadedUrl = await this.uploadImage(img)
              imageUrls.push(uploadedUrl)
            } catch (err) {
              uni.showToast({ title: '图片上传失败', icon: 'none' })
              uni.hideLoading()
              return
            }
          } else {
            imageUrls.push(img)
          }
        }
        
        const res = await uni.request({
          url: `${this.baseUrl}/api/posts/${this.editForm.id}`,
          method: 'PUT',
          data: {
            title: this.editForm.title.trim(),
            content: this.editForm.content.trim(),
            imageUrls: JSON.stringify(imageUrls),
            userId: this.userId
          }
        })
        
        if (res.data.success) {
          uni.showToast({ title: '保存成功', icon: 'success' })
          this.closeEditDialog()
          await this.loadMyPosts()
          
          // 广播帖子更新事件
          uni.$emit('postUpdated', {
            postId: this.editForm.id,
            action: 'update',
            postData: {
              id: this.editForm.id,
              title: this.editForm.title.trim(),
              content: this.editForm.content.trim(),
              imageUrls: JSON.stringify(imageUrls),
              updatedAt: new Date().toISOString()
            }
          })
        } else {
          uni.showToast({ title: res.data.message || '保存失败', icon: 'none' })
        }
      } catch (error) {
        console.error('保存失败:', error)
        uni.showToast({ title: '保存失败', icon: 'none' })
      } finally {
        uni.hideLoading()
      }
    },
    
    async submitEdit() {
      if (!this.editForm.title.trim()) {
        uni.showToast({ title: '请输入标题', icon: 'none' })
        return
      }
      
      if (!this.editForm.content.trim()) {
        uni.showToast({ title: '请输入内容', icon: 'none' })
        return
      }
      
      uni.showLoading({ title: '提交中...' })
      
      try {
        let imageUrls = []
        for (const img of this.editForm.images) {
          if (img.startsWith('http://tmp') || img.startsWith('file://') || img.startsWith('blob:')) {
            try {
              const uploadedUrl = await this.uploadImage(img)
              imageUrls.push(uploadedUrl)
            } catch (err) {
              uni.showToast({ title: '图片上传失败', icon: 'none' })
              uni.hideLoading()
              return
            }
          } else {
            imageUrls.push(img)
          }
        }
        
        const res = await uni.request({
          url: `${this.baseUrl}/api/posts/${this.editForm.id}`,
          method: 'PUT',
          data: {
            title: this.editForm.title.trim(),
            content: this.editForm.content.trim(),
            imageUrls: JSON.stringify(imageUrls),
            userId: this.userId
          }
        })
        
        if (res.data.success) {
          uni.showToast({ 
            title: this.editForm.status === 'draft' ? '发布成功' : '保存成功', 
            icon: 'success' 
          })
          this.closeEditDialog()
          await this.loadMyPosts()
          
          // 广播帖子更新事件
          uni.$emit('postUpdated', {
            postId: this.editForm.id,
            action: this.editForm.status === 'draft' ? 'publish' : 'update',
            postData: {
              id: this.editForm.id,
              title: this.editForm.title.trim(),
              content: this.editForm.content.trim(),
              imageUrls: JSON.stringify(imageUrls),
              updatedAt: new Date().toISOString()
            }
          })
        } else {
          uni.showToast({ title: res.data.message || '提交失败', icon: 'none' })
        }
      } catch (error) {
        console.error('提交失败:', error)
        uni.showToast({ title: '提交失败', icon: 'none' })
      } finally {
        uni.hideLoading()
      }
    },
    
    deletePost(post) {
      uni.showModal({
        title: '删除确认',
        content: `确定要删除"${post.title}"吗？`,
        confirmColor: '#ff4444',
        success: (res) => {
          if (res.confirm) {
            this.performDelete(post.id)
          }
        }
      })
    },
    
    async performDelete(postId) {
      uni.showLoading({ title: '删除中...' })
      try {
        const res = await uni.request({
          url: `${this.baseUrl}/api/posts/${postId}`,
          method: 'DELETE',
          data: { userId: this.userId }
        })
        
        if (res.data.success) {
          this.posts = this.posts.filter(post => post.id !== postId)
          uni.showToast({ title: '删除成功', icon: 'success' })
          
          // 广播帖子删除事件
          uni.$emit('postUpdated', {
            postId: postId,
            action: 'delete'
          })
        } else {
          uni.showToast({ title: res.data.message || '删除失败', icon: 'none' })
        }
      } catch (error) {
        console.error('删除失败:', error)
        uni.showToast({ title: '删除失败', icon: 'none' })
      } finally {
        uni.hideLoading()
      }
    },
    
    createNewPost() {
      uni.navigateTo({ url: '/pages/post/post' })
    },

    formatTime(timestamp) {
      if (!timestamp) return '未知时间'
      const date = new Date(timestamp)
      const now = new Date()
      const diff = now.getTime() - date.getTime()
      
      if (diff < 60000) return '刚刚'
      if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前'
      if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前'
      if (diff < 604800000) return Math.floor(diff / 86400000) + '天前'
      
      const year = date.getFullYear()
      const month = (date.getMonth() + 1).toString().padStart(2, '0')
      const day = date.getDate().toString().padStart(2, '0')
      return `${year}-${month}-${day}`
    }
  }
}
</script>

<style scoped>
/* 样式代码保持不变 */
.my-posts-page {
  min-height: 100vh;
  background-color: #f8f8f8;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15rpx 30rpx;
  background: #fff;
  border-bottom: 1rpx solid #eee;
  position: sticky;
  top: 0;
  z-index: 10;
  height: 88rpx;
  box-sizing: border-box;
}

.nav-icon {
  width: 40rpx;
  height: 40rpx;
}

.nav-title {
  font-size: 36rpx;
  font-weight: 500;
  color: #333;
}

.nav-right {
  display: flex;
  align-items: center;
}

.nav-count {
  font-size: 24rpx;
  color: #999;
}

.content-scroll {
  background: #f8f8f8;
}

.filter-tabs {
  display: flex;
  background: #fff;
  padding: 0 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 24rpx 0;
  font-size: 28rpx;
  color: #666;
  border-bottom: 4rpx solid transparent;
}

.tab-item.active {
  color: #b8d4ff;
  border-bottom-color: #b8d4ff;
  font-weight: 500;
}

.posts-list {
  padding: 20rpx 30rpx;
}

.post-item {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.06);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20rpx;
}

.post-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  flex: 1;
  margin-right: 20rpx;
  line-height: 1.4;
}

.post-status {
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
  flex-shrink: 0;
}

.post-status.published {
  background: #e8f5e8;
  color: #52c41a;
}

.post-status.draft {
  background: #fff7e6;
  color: #fa8c16;
}

.post-content {
  font-size: 28rpx;
  color: #666;
  line-height: 1.6;
  margin-bottom: 20rpx;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-images {
  display: flex;
  gap: 10rpx;
  margin-bottom: 20rpx;
}

.post-image {
  width: 120rpx;
  height: 120rpx;
  border-radius: 8rpx;
  flex-shrink: 0;
}

.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
  padding-top: 20rpx;
  border-top: 1rpx solid #f0f0f0;
}

.post-time {
  font-size: 24rpx;
  color: #999;
}

.post-stats {
  display: flex;
  gap: 30rpx;
}

.stat {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 24rpx;
  color: #999;
}

.stat-icon {
  width: 24rpx;
  height: 24rpx;
}

.post-actions {
  display: flex;
  gap: 20rpx;
  padding-top: 20rpx;
  border-top: 1rpx solid #f0f0f0;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 12rpx 24rpx;
  border-radius: 20rpx;
  font-size: 24rpx;
}

.action-btn.edit {
  background: #e8f1ff;
  color: #b8d4ff;
}

.action-btn.delete {
  background: #ffe8e8;
  color: #ff4444;
}

.action-icon {
  width: 24rpx;
  height: 24rpx;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 0;
  text-align: center;
}

.empty-icon {
  width: 120rpx;
  height: 120rpx;
  opacity: 0.5;
  margin-bottom: 30rpx;
}

.empty-text {
  font-size: 32rpx;
  color: #999;
  margin-bottom: 16rpx;
}

.empty-desc {
  font-size: 26rpx;
  color: #ccc;
  margin-bottom: 40rpx;
}

.empty-btn {
  background: #b8d4ff;
  color: #fff;
  padding: 20rpx 40rpx;
  border-radius: 40rpx;
  font-size: 28rpx;
  font-weight: 500;
}

.floating-btn {
  position: fixed;
  bottom: 140rpx;
  right: 40rpx;
  width: 100rpx;
  height: 100rpx;
  background: #b8d4ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 32rpx rgba(142, 172, 255, 0.3);
  z-index: 999;
}

.btn-icon {
  width: 40rpx;
  height: 40rpx;
}

.dialog-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 1000;
}

.dialog-content {
  background: #fff;
  border-radius: 32rpx 32rpx 0 0;
  width: 100%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.dialog-title {
  font-size: 34rpx;
  font-weight: 600;
  color: #333;
}

.dialog-close {
  font-size: 40rpx;
  color: #999;
  padding: 10rpx;
}

.dialog-body {
  flex: 1;
  padding: 30rpx;
  max-height: 60vh;
}

.form-group {
  margin-bottom: 30rpx;
}

.form-label {
  display: block;
  font-size: 28rpx;
  color: #666;
  margin-bottom: 16rpx;
  font-weight: 500;
}

.form-input {
  width: 100%;
  border: 1rpx solid #e0e0e0;
  border-radius: 12rpx;
  padding: 20rpx;
  font-size: 28rpx;
  box-sizing: border-box;
}

.form-textarea {
  width: 100%;
  border: 1rpx solid #e0e0e0;
  border-radius: 12rpx;
  padding: 20rpx;
  font-size: 28rpx;
  min-height: 200rpx;
  box-sizing: border-box;
}

.image-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
}

.image-item {
  position: relative;
  width: 160rpx;
  height: 160rpx;
}

.upload-image {
  width: 100%;
  height: 100%;
  border-radius: 12rpx;
}

.image-delete {
  position: absolute;
  top: -12rpx;
  right: -12rpx;
  width: 40rpx;
  height: 40rpx;
  background: #ff4444;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 24rpx;
}

.image-add {
  width: 160rpx;
  height: 160rpx;
  border: 2rpx dashed #d0d0d0;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f8f8;
}

.add-icon {
  font-size: 60rpx;
  color: #ccc;
}

.dialog-footer {
  display: flex;
  border-top: 1rpx solid #f0f0f0;
  padding: 20rpx;
  gap: 20rpx;
}

.dialog-btn {
  flex: 1;
  text-align: center;
  padding: 24rpx;
  font-size: 28rpx;
  border-radius: 12rpx;
  background: none;
  border: none;
}

.dialog-btn.cancel {
  background: #f5f5f5;
  color: #666;
}

.dialog-btn.draft {
  background: #fff7e6;
  color: #fa8c16;
}

.dialog-btn.confirm {
  background: #b8d4ff;
  color: #fff;
}
</style>