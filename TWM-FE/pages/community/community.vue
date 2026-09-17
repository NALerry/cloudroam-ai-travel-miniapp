<template>
  <view class="community-page">
    <!-- 搜索栏 -->
    <view class="search-section">
      <view class="search-container">
        <image src="/static/icons/search.png" class="search-icon"></image>
        <input 
          class="search-input" 
          placeholder="搜索社区内容"
          v-model="searchKeyword"
          @confirm="handleSearch"
        />
      </view>
    </view>

    <!-- 社区内容 -->
    <scroll-view class="posts-list" scroll-y @scrolltolower="loadMorePosts">
      <!-- 社区头部 -->
      <view class="community-header">
        <text class="community-title">旅行社区</text>
        <text class="community-desc">发现精彩旅行故事</text>
      </view>

      <!-- 帖子列表 -->
      <view class="posts-container">
        <view 
          class="post-card" 
          v-for="post in allPosts" 
          :key="post.id"
          @tap="viewPostDetail(post)"
        >
          <view class="post-header">
            <image class="author-avatar" :src="post.author.avatar || '/static/avatars/touxiang.png'" mode="aspectFill"></image>
            <view class="author-info">
              <text class="author-name">{{ post.author.name || `用户${post.userId}` }}</text>
              <text class="post-time">{{ formatTime(post.createdAt) }}</text>
            </view>
          </view>
          
          <text class="post-title">{{ post.title }}</text>
          <text class="post-content-preview">{{ post.content }}</text>
          
          <view class="post-images" v-if="post.imagesList && post.imagesList.length > 0">
            <image 
              v-for="(img, index) in post.imagesList.slice(0, 3)" 
              :key="index"
              class="post-image"
              :src="getFullImageUrl(img)"
              mode="aspectFill"
              @tap.stop="previewImages(post.imagesList, index)"
            ></image>
            <text class="image-count" v-if="post.imagesList.length > 3">
              +{{ post.imagesList.length - 3 }}
            </text>
          </view>
          
          <view class="post-footer">
            <view class="post-location" v-if="post.location">
              <image src="/static/icons/general/gps1.png" class="location-icon"></image>
              <text>{{ post.location }}</text>
            </view>
            <view class="post-actions">
              <view class="action-item" @tap.stop="toggleLike(post)">
                <image 
                  :src="post.isLiked ? '/static/icons/general/like1.png' : '/static/icons/general/like.png'" 
                  class="action-icon"
                ></image>
                <text>{{ post.likeCount || 0 }}</text>
              </view>
              <view class="action-item" @tap.stop="goToComments(post)">
                <image src="/static/icons/general/comment.png" class="action-icon"></image>
                <text>{{ post.commentCount || 0 }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <view class="empty-state" v-if="allPosts.length === 0 && !isLoading">
        <image src="/static/icons/empty.png" class="empty-icon"></image>
        <text class="empty-text">暂无帖子，快来发布第一个吧</text>
        <button class="publish-btn" @tap="publishDynamic">发布动态</button>
      </view>

      <!-- 加载更多 -->
      <view class="load-more" v-if="hasMore && allPosts.length > 0 && !isLoading">
        <text class="load-text" @tap="loadMorePosts">{{ isLoading ? '加载中...' : '加载更多' }}</text>
      </view>

      <!-- 加载状态 -->
      <view class="loading-state" v-if="isLoading && allPosts.length === 0">
        <text class="loading-text">加载中...</text>
      </view>
    </scroll-view>

    <!-- 发布弹窗 -->
    <view v-if="showPublishModal" class="publish-modal">
      <view class="modal-mask" @tap="closeModal"></view>
      <view class="modal-content">
        <button class="publish-button" @tap="publishDynamic">发布动态</button>
        <button class="close-button" @tap="closeModal">关闭</button>
      </view>
    </view>

    <!-- 底部导航栏 -->
    <nav-bar current="community" @double-tap="showPublishModal = true" />
  </view>
</template>

<script>
export default {
  data() {
    return {
      currentPage: 'community',
      showPublishModal: false,
      allPosts: [],
      searchKeyword: '',
      isLoading: false,
      hasMore: true,
      currentPageNum: 1,
      pageSize: 10,
      baseUrl: 'http://localhost:8080'
    }
  },
  onLoad() {
    this.loadPosts()
    
    uni.$on('commentAdded', this.handleCommentAdded)
    uni.$on('likeToggled', this.handleLikeToggled)
    uni.$on('postUpdated', this.handlePostUpdated)
  },
  onUnload() {
    uni.$off('commentAdded', this.handleCommentAdded)
    uni.$off('likeToggled', this.handleLikeToggled)
    uni.$off('postUpdated', this.handlePostUpdated)
  },
  onPullDownRefresh() {
    this.refreshPosts()
  },
  onShow() {
    this.refreshPosts()
  },
  methods: {
    getFullImageUrl(url) {
      if (!url) return ''
      if (url.startsWith('http://') || url.startsWith('https://')) {
        return url
      }
      if (url.startsWith('/uploads/')) {
        return this.baseUrl + url
      }
      return url
    },

    handlePostUpdated(data) {
      console.log('community页面收到帖子更新事件:', data)
      
      if (data.action === 'delete') {
        const index = this.allPosts.findIndex(p => p.id === data.postId)
        if (index !== -1) {
          this.allPosts.splice(index, 1)
          uni.showToast({ title: '帖子已删除', icon: 'success' })
        }
      } else {
        this.refreshSinglePost(data.postId)
      }
    },

    async refreshSinglePost(postId) {
      try {
        const res = await this.apiRequest(`/posts/${postId}`, 'GET')
        
        if (res.statusCode === 200 && res.data && res.data.success) {
          const post = res.data.data
          const processedPosts = this.processPostsData([post])
          
          if (processedPosts.length > 0) {
            const updatedPost = processedPosts[0]
            
            const userInfo = uni.getStorageSync('user_info')
            if (userInfo && userInfo.id) {
              try {
                const likeRes = await this.apiRequest(`/likes/user/${userInfo.id}/check/${postId}`, 'GET')
                if (likeRes.statusCode === 200 && likeRes.data && likeRes.data.success) {
                  updatedPost.isLiked = likeRes.data.liked
                }
              } catch (error) {
                console.error('检查点赞状态失败:', error)
              }
            }
            
            const index = this.allPosts.findIndex(p => p.id === postId)
            if (index !== -1) {
              this.$set(this.allPosts, index, updatedPost)
              uni.showToast({ title: '内容已更新', icon: 'success' })
            } else {
              this.allPosts.unshift(updatedPost)
              uni.showToast({ title: '新帖子已添加', icon: 'success' })
            }
          }
        }
      } catch (error) {
        console.error('刷新帖子失败:', error)
      }
    },

    handleCommentAdded(data) {
      const { postId, commentCount } = data
      const post = this.allPosts.find(item => item.id === postId)
      if (post) {
        post.commentCount = commentCount
      }
    },

    handleLikeToggled(data) {
      const { postId, likeCount, isLiked } = data
      const post = this.allPosts.find(item => item.id === postId)
      if (post) {
        post.likeCount = likeCount
        post.isLiked = isLiked
      }
    },

    async apiRequest(url, method = 'GET', data = null) {
      try {
        const config = {
          url: `${this.baseUrl}/api${url}`,
          method: method,
          timeout: 10000,
          header: {
            'Content-Type': 'application/json'
          }
        }
        
        if (method === 'GET' && data) {
          // 对于GET请求，将参数拼接到URL
          const params = new URLSearchParams(data).toString()
          config.url = `${config.url}?${params}`
        } else if (data) {
          config.data = data
        }
        
        console.log(`发送${method}请求到: ${config.url}`)
        const res = await uni.request(config)
        console.log(`响应状态: ${res.statusCode}`, res.data)
        
        return res
      } catch (error) {
        console.error('API请求失败:', error)
        throw error
      }
    },

    async loadPosts() {
      if (this.isLoading) return
      
      this.isLoading = true
      try {
        const params = {
          page: this.currentPageNum,
          size: this.pageSize
        }
        
        if (this.searchKeyword.trim()) {
          params.keyword = this.searchKeyword.trim()
        }
        
        const res = await this.apiRequest('/posts', 'GET', params)
        
        if (res.statusCode === 200 && res.data && res.data.success) {
          let postsData = res.data.data
          let posts = []
          
          // 处理不同的响应结构
          if (Array.isArray(postsData)) {
            posts = postsData
          } else if (postsData.content) {
            posts = postsData.content
          } else if (postsData.data) {
            posts = postsData.data
          } else {
            posts = postsData
          }
          
          const processedPosts = this.processPostsData(posts)
          
          if (this.currentPageNum === 1) {
            this.allPosts = processedPosts
          } else {
            this.allPosts = [...this.allPosts, ...processedPosts]
          }
          
          // 判断是否还有更多数据
          if (postsData.totalPages) {
            this.hasMore = this.currentPageNum < postsData.totalPages
          } else {
            this.hasMore = processedPosts.length === this.pageSize
          }
          
          // 检查点赞状态
          await this.checkPostsLikeStatus()
        } else {
          console.error('加载失败:', res.data)
          uni.showToast({
            title: res.data?.message || '加载失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('加载帖子失败:', error)
        uni.showToast({
          title: '网络错误',
          icon: 'none'
        })
      } finally {
        this.isLoading = false
        uni.stopPullDownRefresh()
      }
    },

    async checkPostsLikeStatus() {
      const userInfo = uni.getStorageSync('user_info')
      if (!userInfo || !userInfo.id) return

      for (let post of this.allPosts) {
        try {
          const res = await this.apiRequest(`/likes/user/${userInfo.id}/check/${post.id}`, 'GET')
          
          if (res.statusCode === 200 && res.data && res.data.success) {
            post.isLiked = res.data.liked
          }
        } catch (error) {
          console.error('检查点赞状态失败:', error)
        }
      }
    },

    processPostsData(posts) {
      if (!posts || !Array.isArray(posts)) return []
      
      return posts.map(post => {
        // 处理图片数据
        let imagesList = []
        if (post.imageUrls) {
          if (Array.isArray(post.imageUrls)) {
            imagesList = post.imageUrls
          } else if (typeof post.imageUrls === 'string') {
            try {
              const parsed = JSON.parse(post.imageUrls)
              if (Array.isArray(parsed)) {
                imagesList = parsed
              } else {
                imagesList = post.imageUrls.split(',').filter(url => url && url.trim())
              }
            } catch (e) {
              imagesList = post.imageUrls.split(',').filter(url => url && url.trim())
            }
          }
        }
        
        // 处理作者信息
        let authorInfo = {
          name: '匿名用户',
          avatar: '/static/avatars/touxiang.png'
        }
        
        if (post.author) {
          authorInfo = {
            name: post.author.nickname || post.author.username || '匿名用户',
            avatar: this.getFullImageUrl(post.author.avatar) || '/static/avatars/touxiang.png'
          }
        } else if (post.userId) {
          authorInfo.name = `用户${post.userId}`
        }
        
        return {
          ...post,
          imagesList: imagesList,
          author: authorInfo,
          likeCount: post.likeCount || 0,
          commentCount: post.commentCount || 0,
          isLiked: false
        }
      })
    },

    async refreshPosts() {
      this.currentPageNum = 1
      this.allPosts = []
      await this.loadPosts()
      uni.showToast({
        title: '刷新成功',
        icon: 'success'
      })
    },

    async loadMorePosts() {
      if (this.isLoading || !this.hasMore) return
      
      this.currentPageNum++
      await this.loadPosts()
    },

    handleSearch() {
      this.currentPageNum = 1
      this.allPosts = []
      this.loadPosts()
    },

    viewPostDetail(post) {
      this.updatePostViewCount(post.id)
      
      uni.navigateTo({
        url: `/pages/post-detail/post-detail?id=${post.id}`,
        fail: (err) => {
          console.error('跳转失败:', err)
          uni.showToast({
            title: '跳转失败',
            icon: 'none'
          })
        }
      })
    },

    async updatePostViewCount(postId) {
      try {
        await this.apiRequest(`/posts/${postId}/view`, 'POST')
      } catch (error) {
        console.error('更新浏览计数失败:', error)
      }
    },

    previewImages(images, currentIndex) {
      if (!images || images.length === 0) return
      
      const fullUrls = images.map(img => this.getFullImageUrl(img))
      uni.previewImage({
        current: currentIndex,
        urls: fullUrls
      })
    },

    async toggleLike(post) {
      try {
        const userInfo = uni.getStorageSync('user_info')
        if (!userInfo || !userInfo.id) {
          uni.showToast({ title: '请先登录', icon: 'none' })
          setTimeout(() => {
            uni.navigateTo({
              url: '/pages/login/login'
            })
          }, 1500)
          return
        }

        // 乐观更新
        const wasLiked = post.isLiked
        const oldCount = post.likeCount
        
        post.isLiked = !wasLiked
        post.likeCount = wasLiked ? Math.max(0, oldCount - 1) : oldCount + 1
        
        let url, method, requestData
        
        if (post.isLiked) {
          url = '/likes'
          method = 'POST'
          requestData = {
            userId: userInfo.id,
            postId: post.id
          }
        } else {
          url = `/likes/user/${userInfo.id}/post/${post.id}`
          method = 'DELETE'
          requestData = null
        }
        
        const res = await this.apiRequest(url, method, requestData)
        
        if (res.statusCode === 200 && res.data && res.data.success) {
          uni.$emit('likeToggled', {
            postId: post.id,
            likeCount: post.likeCount,
            isLiked: post.isLiked
          })
          
          uni.showToast({
            title: post.isLiked ? '点赞成功' : '取消点赞',
            icon: 'success',
            duration: 1000
          })
        } else {
          // 回滚
          post.isLiked = wasLiked
          post.likeCount = oldCount
          throw new Error(res.data?.message || '操作失败')
        }
      } catch (error) {
        console.error('点赞操作失败:', error)
        uni.showToast({
          title: '操作失败',
          icon: 'none'
        })
      }
    },

    goToComments(post) {
      uni.navigateTo({
        url: `/pages/post-detail/post-detail?id=${post.id}&mode=comment`,
        fail: (err) => {
          console.error('跳转失败:', err)
          uni.showToast({
            title: '跳转失败',
            icon: 'none'
          })
        }
      })
    },

    publishDynamic() {
      this.closeModal()
      uni.navigateTo({
        url: '/pages/publish/publish'
      })
    },

    closeModal() {
      this.showPublishModal = false
    },

    formatTime(timestamp) {
      if (!timestamp) return '未知时间'
      
      let date
      if (typeof timestamp === 'string') {
        date = new Date(timestamp)
      } else {
        date = new Date(timestamp)
      }
      
      if (isNaN(date.getTime())) {
        return '未知时间'
      }
      
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
.community-page {
  min-height: 100vh;
  background-color: #f8f8f8;
  padding-bottom: 120rpx;
}

.search-section {
  padding: 20rpx 30rpx;
  background: #fff;
  border-bottom: 1rpx solid #f0f0f0;
}

.search-container {
  display: flex;
  align-items: center;
  background: #f8f8f8;
  border-radius: 50rpx;
  padding: 12rpx 20rpx;
}

.search-icon {
  width: 40rpx;
  height: 40rpx;
  margin-right: 16rpx;
}

.search-input {
  flex: 1;
  font-size: 28rpx;
  height: 60rpx;
}

.posts-list {
  height: calc(100vh - 120rpx);
}

.posts-container {
  padding: 20rpx 30rpx;
}

.community-header {
  text-align: center;
  padding: 40rpx 0;
}

.community-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
  display: block;
  margin-bottom: 12rpx;
}

.community-desc {
  font-size: 26rpx;
  color: #999;
}

.post-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
}

.post-header {
  display: flex;
  align-items: center;
  margin-bottom: 24rpx;
}

.author-avatar {
  width: 60rpx;
  height: 60rpx;
  border-radius: 30rpx;
  margin-right: 16rpx;
}

.author-info {
  flex: 1;
}

.author-name {
  font-size: 28rpx;
  font-weight: 500;
  color: #333;
  display: block;
  margin-bottom: 4rpx;
}

.post-time {
  font-size: 22rpx;
  color: #999;
}

.post-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  display: block;
  margin-bottom: 16rpx;
  line-height: 1.4;
}

.post-content-preview {
  font-size: 28rpx;
  color: #666;
  line-height: 1.6;
  display: block;
  margin-bottom: 24rpx;
}

.post-images {
  display: flex;
  gap: 10rpx;
  margin-bottom: 24rpx;
  flex-wrap: wrap;
}

.post-image {
  width: 200rpx;
  height: 200rpx;
  border-radius: 12rpx;
  flex-shrink: 0;
}

.image-count {
  width: 200rpx;
  height: 200rpx;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
}

.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.post-location {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 24rpx;
  color: #999;
}

.location-icon {
  width: 24rpx;
  height: 24rpx;
}

.post-actions {
  display: flex;
  gap: 30rpx;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 24rpx;
  color: #999;
}

.action-icon {
  width: 32rpx;
  height: 32rpx;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx 30rpx;
  text-align: center;
}

.empty-icon {
  width: 120rpx;
  height: 120rpx;
  margin-bottom: 30rpx;
  opacity: 0.5;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
  margin-bottom: 40rpx;
}

.publish-btn {
  background: #b8d4ff;
  color: #fff;
  border: none;
  border-radius: 40rpx;
  padding: 20rpx 40rpx;
  font-size: 28rpx;
}

.load-more {
  text-align: center;
  padding: 40rpx;
}

.load-text {
  font-size: 28rpx;
  color: #b8d4ff;
}

.loading-state {
  text-align: center;
  padding: 40rpx;
}

.loading-text {
  font-size: 28rpx;
  color: #999;
}

.publish-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
}

.modal-mask {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
}

.modal-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  border-radius: 20rpx 20rpx 0 0;
  padding: 40rpx 30rpx;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.publish-button {
  background: #b8d4ff;
  color: #fff;
  border: none;
  border-radius: 40rpx;
  padding: 24rpx;
  font-size: 28rpx;
}

.close-button {
  background: #f8f8f8;
  color: #666;
  border: none;
  border-radius: 40rpx;
  padding: 24rpx;
  font-size: 28rpx;
}
</style>