<template>
  <view class="post-page">
    <!-- 搜索栏 -->
    <view class="search-section">
      <view class="search-container">
        <image src="/static/icons/search.png" class="search-icon"></image>
        <input 
          class="search-input" 
          placeholder="搜索投稿内容或地点"
          @confirm="onSearch"
          v-model="searchKeyword"
        />
      </view>
    </view>

    <!-- 社区内容区域 -->
    <view class="community-content" v-if="!showQuickPost">
      <view class="community-header">
        <text class="community-title">旅行社区</text>
        <text class="community-desc">发现精彩旅行故事</text>
      </view>

      <!-- 帖子列表 -->
      <view class="posts-list">
        <view 
          class="post-card" 
          v-for="post in communityPosts" 
          :key="post.id"
          @tap="viewPostDetail(post)"
        >
          <view class="post-header">
            <image class="author-avatar" :src="getAvatarUrl(post.author?.avatar)" mode="aspectFill"></image>
            <view class="author-info">
              <text class="author-name">{{ post.author?.name || '匿名用户' }}</text>
              <text class="post-time">{{ post.createTime }}</text>
            </view>
          </view>
          
          <text class="post-title">{{ post.title }}</text>
          <text class="post-content-preview">{{ post.content }}</text>
          
          <view class="post-images" v-if="post.images && post.images.length > 0">
            <image 
              v-for="(img, index) in post.images.slice(0, 3)" 
              :key="index"
              class="post-image"
              :src="getFullImageUrl(img)"
              mode="aspectFill"
              @tap.stop="previewPostImages(post.images, index)"
            ></image>
            <text class="image-count" v-if="post.images.length > 3">
              +{{ post.images.length - 3 }}
            </text>
          </view>
          
          <view class="post-footer">
            <view class="post-location" v-if="post.location">
              <image src="/static/icons/general/gps1.png" class="custom-icon"></image>
              <text>{{ post.location }}</text>
            </view>
            <view class="post-actions">
              <view class="action-item" @tap.stop="toggleCollect(post)" :class="{'active': post.isCollected}">
                <image 
                  :src="post.isCollected ? '/static/icons/general/favorite1.png' : '/static/icons/general/favorite.png'" 
                  class="custom-icon"
                ></image>
                <text>{{ post.collectCount || 0 }}</text>
              </view>
              <view class="action-item" :class="{'active': post.isLiked}">
                <image 
                  :src="post.isLiked ? '/static/icons/general/like1.png' : '/static/icons/general/like.png'" 
                  class="custom-icon"
                  @tap.stop="toggleLike(post)"
                ></image>
                <text>{{ post.likeCount }}</text>
              </view>
              <view class="action-item" @tap.stop="goToComment(post)">
                <image src="/static/icons/general/comment.png" class="custom-icon"></image>
                <text>{{ post.commentCount || 0 }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <view class="empty-state" v-if="communityPosts.length === 0 && !isLoading">
        <image src="/static/icons/empty.png" class="empty-icon"></image>
        <text class="empty-text">暂无帖子，快来发布第一个吧</text>
      </view>

      <!-- 加载状态 -->
      <view class="loading-state" v-if="isLoading && communityPosts.length === 0">
        <text class="loading-text">加载中...</text>
      </view>

      <!-- 加载更多 -->
      <view class="load-more" v-if="hasMorePosts && communityPosts.length > 0 && !isLoading">
        <text class="load-text" @tap="loadMorePosts">加载更多</text>
      </view>
    </view>

    <!-- 快速发布弹窗 -->
    <view class="quick-post-modal" v-if="showQuickPost" @tap="closeQuickPost">
      <view class="modal-content" @tap.stop>
        <view class="modal-header">
          <text class="modal-title">快速发布</text>
          <image src="/static/icons/close.png" class="custom-icon" @tap="closeQuickPost"></image>
        </view>
        
        <view class="quick-form">
          <!-- 标题输入框 -->
          <input 
            class="quick-title" 
            v-model="quickPost.title"
            placeholder="标题（可选，不填将自动生成）"
            maxlength="50"
          />
          
          <textarea 
            class="quick-content" 
            v-model="quickPost.content"
            placeholder="分享你的旅行瞬间..."
            maxlength="200"
            auto-height
          />
          <text class="char-count">{{ quickPost.content.length }}/200</text>
          
          <view class="quick-actions">
            <view class="action-btn" @tap="addQuickImage">
              <image src="/static/icons/general/photography.png" class="custom-icon"></image>
            </view>
            <view class="action-btn" @tap="addLocation">
              <image src="/static/icons/general/gps.png" class="custom-icon"></image>
            </view>
          </view>
          
          <view class="quick-images" v-if="quickPost.images.length > 0">
            <view 
              class="quick-image-item" 
              v-for="(image, index) in quickPost.images" 
              :key="index"
            >
              <image :src="image" mode="aspectFill" class="image-preview"></image>
              <view class="remove-image" @tap="removeQuickImage(index)">
                <image src="/static/icons/close.png" class="custom-icon"></image>
              </view>
            </view>
          </view>
          
          <view class="quick-submit">
            <button 
              class="submit-btn" 
              :disabled="!quickPost.content.trim()"
              @tap="submitQuickPost"
            >
              发布
            </button>
          </view>
        </view>
      </view>
    </view>

    <!-- 悬浮操作按钮 -->
    <view class="floating-action-btn" @tap="openQuickPost">
      <view class="fab-icon">
        <image src="/static/icons/general/edit.png" class="custom-icon large-icon"></image>
      </view>
    </view>
  </view>
</template>

<script>
// ============ 配置区域 ============
const TENCENT_MAP_KEY = 'HETBZ-KJFO7-2UPXM-HLRLV-S75H7-TOBNA'
// =================================

export default {
  data() {
    return {
      searchKeyword: '',
      showQuickPost: false,
      communityPosts: [],
      hasMorePosts: true,
      quickPost: {
        title: '',
        content: '',
        images: [],
        location: ''
      },
      currentPage: 1,
      pageSize: 10,
      isLoading: false,
      locationLoading: false,
      baseUrl: 'http://localhost:8080'
    }
  },
  onLoad() {
    this.loadCommunityPosts()
    uni.$on('collectionStatusChanged', this.handleCollectionStatusChanged)
    uni.$on('likeStatusChanged', this.handleLikeStatusChanged)
    uni.$on('postUpdated', this.handlePostUpdated)
  },
  onUnload() {
    uni.$off('collectionStatusChanged', this.handleCollectionStatusChanged)
    uni.$off('likeStatusChanged', this.handleLikeStatusChanged)
    uni.$off('postUpdated', this.handlePostUpdated)
  },
  onPullDownRefresh() {
    this.refreshPosts()
  },
  onReachBottom() {
    this.loadMorePosts()
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

    getAvatarUrl(avatar) {
      if (!avatar) return '/static/images/default-avatar.png'
      if (avatar.startsWith('http')) return avatar
      if (avatar.startsWith('/uploads/')) return this.baseUrl + avatar
      return avatar
    },
    
    handleCollectionStatusChanged(data) {
      const post = this.communityPosts.find(p => p.id === data.postId)
      if (post) {
        post.isCollected = data.isCollected
        post.collectCount = data.collectCount
        this.$forceUpdate()
      }
    },

    handleLikeStatusChanged(data) {
      const post = this.communityPosts.find(p => p.id === data.postId)
      if (post) {
        post.isLiked = data.isLiked
        post.likeCount = data.likeCount
        this.$forceUpdate()
      }
    },

    handlePostUpdated(data) {
      console.log('收到帖子更新事件:', data)
      
      if (data.action === 'delete') {
        const index = this.communityPosts.findIndex(p => p.id === data.postId)
        if (index !== -1) {
          this.communityPosts.splice(index, 1)
          uni.showToast({ title: '帖子已删除', icon: 'success' })
        }
      } else {
        this.refreshSinglePost(data.postId)
      }
    },

    async refreshSinglePost(postId) {
      try {
        const userInfo = uni.getStorageSync('user_info')
        const userId = userInfo ? userInfo.id : null
        
        const res = await this.$http.get(`/api/posts/${postId}`)
        
        if (res.data.success) {
          const post = res.data.data
          
          let isCollected = false
          let isLiked = false
          
          if (userId) {
            try {
              const collectionRes = await this.$http.get(`/api/collections/user/${userId}/check/${postId}`)
              isCollected = collectionRes.data.collected
              const likeRes = await this.$http.get(`/api/likes/user/${userId}/check/${postId}`)
              isLiked = likeRes.data.liked
            } catch (error) {
              console.error('检查状态失败:', error)
            }
          }
          
          let images = []
          if (post.imageUrls) {
            if (Array.isArray(post.imageUrls)) {
              images = post.imageUrls
            } else if (typeof post.imageUrls === 'string') {
              try {
                const parsed = JSON.parse(post.imageUrls)
                if (Array.isArray(parsed)) {
                  images = parsed
                } else {
                  images = post.imageUrls.split(',').filter(url => url && url.trim())
                }
              } catch (e) {
                images = post.imageUrls.split(',').filter(url => url && url.trim())
              }
            }
          }
          
          images = images.map(img => this.getFullImageUrl(img))
          
          const authorInfo = {
            name: post.author?.nickname || post.author?.username || '匿名用户',
            avatar: this.getAvatarUrl(post.author?.avatar)
          }
          
          const updatedPost = {
            ...post,
            images: images,
            isLiked: isLiked,
            isCollected: isCollected,
            author: authorInfo,
            createTime: this.formatTime(post.createdAt),
            commentCount: post.commentCount || 0,
            collectCount: isCollected ? Math.max(1, post.collectCount || 0) : (post.collectCount || 0),
            likeCount: isLiked ? Math.max(1, post.likeCount || 0) : (post.likeCount || 0)
          }
          
          const index = this.communityPosts.findIndex(p => p.id === postId)
          if (index !== -1) {
            this.$set(this.communityPosts, index, updatedPost)
            uni.showToast({ title: '内容已更新', icon: 'success' })
          } else {
            this.communityPosts.unshift(updatedPost)
            uni.showToast({ title: '新帖子已添加', icon: 'success' })
          }
        }
      } catch (error) {
        console.error('刷新帖子失败:', error)
      }
    },

    onSearch() {
      if (this.searchKeyword.trim()) {
        uni.navigateTo({
          url: `/pages/search/search?keyword=${encodeURIComponent(this.searchKeyword)}&type=post`
        })
      }
    },

    async loadCommunityPosts() {
      try {
        this.isLoading = true
        const userInfo = uni.getStorageSync('user_info')
        const userId = userInfo ? userInfo.id : null
        
        console.log('开始加载帖子，页码:', this.currentPage)
        
        const res = await this.$http.get('/api/posts', {
          page: this.currentPage,
          size: this.pageSize
        })
        
        console.log('API响应:', res.data)
        
        if (res.data && res.data.success) {
          let posts = []
          if (Array.isArray(res.data.data)) {
            posts = res.data.data
          } else if (res.data.data && Array.isArray(res.data.data.content)) {
            posts = res.data.data.content
          } else if (res.data.data && Array.isArray(res.data.data.data)) {
            posts = res.data.data.data
          } else {
            posts = res.data.data || []
          }
          
          console.log('解析后的帖子数量:', posts.length)
          
          const postsWithStatus = await Promise.all(
            posts.map(async (post) => {
              let isCollected = false
              let isLiked = false
              
              if (userId) {
                try {
                  const collectionRes = await this.$http.get(`/api/collections/user/${userId}/check/${post.id}`)
                  isCollected = collectionRes.data.collected
                  const likeRes = await this.$http.get(`/api/likes/user/${userId}/check/${post.id}`)
                  isLiked = likeRes.data.liked
                } catch (error) {
                  console.error('检查状态失败:', error)
                }
              }
              
              let images = []
              if (post.imageUrls) {
                if (Array.isArray(post.imageUrls)) {
                  images = post.imageUrls
                } else if (typeof post.imageUrls === 'string') {
                  try {
                    const parsed = JSON.parse(post.imageUrls)
                    if (Array.isArray(parsed)) {
                      images = parsed
                    } else {
                      images = post.imageUrls.split(',').filter(url => url && url.trim())
                    }
                  } catch (e) {
                    images = post.imageUrls.split(',').filter(url => url && url.trim())
                  }
                }
              }
              
              images = images.map(img => this.getFullImageUrl(img))
              
              const authorInfo = {
                name: post.author?.nickname || post.author?.username || '匿名用户',
                avatar: this.getAvatarUrl(post.author?.avatar)
              }
              
              return {
                ...post,
                images: images,
                isLiked: isLiked,
                isCollected: isCollected,
                author: authorInfo,
                createTime: this.formatTime(post.createdAt),
                commentCount: post.commentCount || 0,
                collectCount: isCollected ? Math.max(1, post.collectCount || 0) : (post.collectCount || 0),
                likeCount: isLiked ? Math.max(1, post.likeCount || 0) : (post.likeCount || 0)
              }
            })
          )

          if (this.currentPage === 1) {
            this.communityPosts = postsWithStatus
          } else {
            this.communityPosts = [...this.communityPosts, ...postsWithStatus]
          }
          
          if (res.data.data && res.data.data.totalPages) {
            this.hasMorePosts = this.currentPage < res.data.data.totalPages
          } else if (res.data.hasNext !== undefined) {
            this.hasMorePosts = res.data.hasNext
          } else {
            this.hasMorePosts = postsWithStatus.length === this.pageSize
          }
          
          console.log('加载完成，帖子数量:', this.communityPosts.length, '是否有更多:', this.hasMorePosts)
        } else {
          console.error('API返回失败:', res.data)
          uni.showToast({ title: res.data?.message || '加载失败', icon: 'none' })
        }
        
        uni.stopPullDownRefresh()
      } catch (error) {
        console.error('加载帖子失败:', error)
        uni.stopPullDownRefresh()
        uni.showToast({ title: '网络错误: ' + (error.message || '请检查网络'), icon: 'none' })
      } finally {
        this.isLoading = false
      }
    },

    async refreshPosts() {
      this.currentPage = 1
      await this.loadCommunityPosts()
      uni.showToast({ title: '刷新成功', icon: 'success' })
    },

    loadMorePosts() {
      if (!this.hasMorePosts || this.isLoading) return
      this.currentPage++
      this.loadCommunityPosts()
    },

    viewPostDetail(post) {
      uni.navigateTo({ url: `/pages/post-detail/post-detail?id=${post.id}` })
    },

    previewPostImages(images, currentIndex) {
      const fullUrls = images.map(img => this.getFullImageUrl(img))
      uni.previewImage({ current: currentIndex, urls: fullUrls })
    },

    async toggleLike(post) {
      try {
        const userInfo = uni.getStorageSync('user_info')
        if (!userInfo || !userInfo.id) {
          uni.showToast({ title: '请先登录', icon: 'none' })
          uni.navigateTo({ url: '/pages/login/login' })
          return
        }

        const wasLiked = post.isLiked
        const oldCount = post.likeCount || 0
        
        post.isLiked = !wasLiked
        post.likeCount = wasLiked ? Math.max(0, oldCount - 1) : Math.max(1, oldCount + 1)

        if (wasLiked) {
          await this.$http.delete(`/api/likes/user/${userInfo.id}/post/${post.id}`)
          uni.showToast({ title: '已取消点赞', icon: 'success' })
          if (post.likeCount < 0) post.likeCount = 0
        } else {
          await this.$http.post('/api/likes', { userId: userInfo.id, postId: post.id })
          uni.showToast({ title: '点赞成功', icon: 'success' })
        }
        
        this.$forceUpdate()
        uni.$emit('likeStatusChanged', {
          postId: post.id,
          isLiked: post.isLiked,
          likeCount: post.likeCount
        })
        
      } catch (error) {
        console.error('点赞操作失败:', error)
        uni.showToast({ title: '操作失败，请重试', icon: 'none' })
      }
    },

    async toggleCollect(post) {
      try {
        const userInfo = uni.getStorageSync('user_info')
        if (!userInfo || !userInfo.id) {
          uni.showToast({ title: '请先登录', icon: 'none' })
          uni.navigateTo({ url: '/pages/login/login' })
          return
        }

        const wasCollected = post.isCollected
        const oldCount = post.collectCount || 0
        
        post.isCollected = !wasCollected
        post.collectCount = wasCollected ? Math.max(0, oldCount - 1) : Math.max(1, oldCount + 1)

        if (wasCollected) {
          const result = await this.$http.delete(`/api/collections/user/${userInfo.id}/post/${post.id}`)
          if (result.data.success) {
            uni.showToast({ title: '已取消收藏', icon: 'success' })
            if (post.collectCount < 0) post.collectCount = 0
          } else {
            post.isCollected = wasCollected
            post.collectCount = oldCount
            throw new Error('取消收藏失败')
          }
        } else {
          const result = await this.$http.post('/api/collections', { userId: userInfo.id, postId: post.id })
          if (result.data.success) {
            uni.showToast({ title: '收藏成功', icon: 'success' })
          } else {
            post.isCollected = wasCollected
            post.collectCount = oldCount
            throw new Error('收藏失败')
          }
        }
        
        this.$forceUpdate()
        uni.$emit('collectionStatusChanged', {
          postId: post.id,
          isCollected: post.isCollected,
          collectCount: post.collectCount
        })
        
      } catch (error) {
        console.error('收藏操作失败:', error)
        uni.showToast({ title: '操作失败，请重试', icon: 'none' })
      }
    },

    goToComment(post) {
      uni.navigateTo({ url: `/pages/post-detail/post-detail?id=${post.id}&mode=comment` })
    },

    openQuickPost() {
      const userInfo = uni.getStorageSync('user_info')
      if (!userInfo || !userInfo.id) {
        uni.showToast({ title: '请先登录', icon: 'none' })
        uni.navigateTo({ url: '/pages/login/login' })
        return
      }
      this.showQuickPost = true
    },

    closeQuickPost() {
      this.showQuickPost = false
      this.quickPost = { title: '', content: '', images: [], location: '' }
    },

    addQuickImage() {
      uni.chooseImage({
        count: 9 - this.quickPost.images.length,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
        success: (res) => {
          this.quickPost.images = [...this.quickPost.images, ...res.tempFilePaths]
        }
      })
    },

    removeQuickImage(index) {
      this.quickPost.images.splice(index, 1)
    },

    async addLocation() {
      const userInfo = uni.getStorageSync('user_info')
      if (!userInfo || !userInfo.id) {
        uni.showToast({ title: '请先登录', icon: 'none' })
        uni.navigateTo({ url: '/pages/login/login' })
        return
      }

      const hasPermission = await this.checkLocationPermission()
      if (!hasPermission) return

      uni.showLoading({ title: '定位中...', mask: true })
      this.locationLoading = true

      try {
        const location = await this.getCurrentLocation()
        const address = await this.getAddressByTencentMap(location)
        
        if (address) {
          this.quickPost.location = address
          uni.showToast({ title: '定位成功', icon: 'success' })
        } else {
          throw new Error('获取地址失败')
        }
      } catch (error) {
        console.error('定位失败:', error)
        this.fallbackChooseLocation()
      } finally {
        uni.hideLoading()
        this.locationLoading = false
      }
    },

    checkLocationPermission() {
      return new Promise((resolve) => {
        uni.getSetting({
          success: (res) => {
            if (res.authSetting['scope.userLocation']) {
              resolve(true)
            } else {
              uni.authorize({
                scope: 'scope.userLocation',
                success: () => resolve(true),
                fail: () => {
                  uni.showModal({
                    title: '位置权限',
                    content: '需要获取您的位置信息来标记发帖地点',
                    confirmText: '去设置',
                    success: (modalRes) => {
                      if (modalRes.confirm) {
                        uni.openSetting()
                      }
                      resolve(false)
                    }
                  })
                }
              })
            }
          },
          fail: () => resolve(false)
        })
      })
    },

    getCurrentLocation() {
      return new Promise((resolve, reject) => {
        uni.getLocation({
          type: 'gcj02',
          success: (res) => {
            resolve({
              latitude: res.latitude,
              longitude: res.longitude
            })
          },
          fail: (err) => {
            reject(err)
          }
        })
      })
    },

    async getAddressByTencentMap(location) {
      try {
        const url = `https://apis.map.qq.com/ws/geocoder/v1/`
        const res = await uni.request({
          url: url,
          data: {
            location: `${location.latitude},${location.longitude}`,
            key: TENCENT_MAP_KEY,
            get_poi: 0
          }
        })

        if (res.statusCode === 200 && res.data.status === 0) {
          const result = res.data.result
          const address = result.formatted_addresses?.recommend || result.address
          console.log('腾讯地图返回地址:', address)
          return address
        } else {
          console.error('腾讯地图API错误:', res.data)
          return null
        }
      } catch (error) {
        console.error('腾讯地图请求失败:', error)
        return null
      }
    },

    fallbackChooseLocation() {
      uni.showModal({
        title: '定位失败',
        content: '自动定位失败，是否手动选择位置？',
        confirmText: '手动选择',
        cancelText: '取消',
        success: (res) => {
          if (res.confirm) {
            uni.chooseLocation({
              success: (chooseRes) => {
                this.quickPost.location = chooseRes.name || chooseRes.address
                uni.showToast({ title: '选择成功', icon: 'success' })
              },
              fail: () => {
                uni.showToast({ title: '取消选择', icon: 'none' })
              }
            })
          }
        }
      })
    },

    // 生成智能标题
    generateSmartTitle(content) {
      const trimmedContent = content.trim().replace(/\s+/g, ' ')
      
      if (trimmedContent.length <= 30) {
        return trimmedContent
      }
      
      const firstSentenceMatch = trimmedContent.match(/^[^。！？\n]+[。！？\n]/)
      if (firstSentenceMatch && firstSentenceMatch[0].length <= 35) {
        return firstSentenceMatch[0].trim()
      }
      
      let title = trimmedContent.substring(0, 30)
      
      const lastSpaceIndex = title.lastIndexOf(' ')
      const lastPunctuationIndex = Math.max(
        title.lastIndexOf('，'),
        title.lastIndexOf('、'),
        title.lastIndexOf('；')
      )
      
      if (lastPunctuationIndex > title.length * 0.6) {
        title = title.substring(0, lastPunctuationIndex + 1)
      } else if (lastSpaceIndex > title.length * 0.6) {
        title = title.substring(0, lastSpaceIndex)
      }
      
      return title + '...'
    },

    async submitQuickPost() {
      if (!this.quickPost.content.trim()) {
        uni.showToast({ title: '请输入内容', icon: 'none' })
        return
      }

      const userInfo = uni.getStorageSync('user_info')
      if (!userInfo || !userInfo.id) {
        uni.showToast({ title: '请先登录', icon: 'none' })
        uni.navigateTo({ url: '/pages/login/login' })
        return
      }

      uni.showLoading({ title: '发布中...' })

      try {
        let title = this.quickPost.title.trim()
        if (!title) {
          title = this.generateSmartTitle(this.quickPost.content)
        }
        
        const postData = {
          title: title,
          content: this.quickPost.content,
          imageUrls: this.quickPost.images.length > 0 ? JSON.stringify(this.quickPost.images) : null,
          location: this.quickPost.location || null,
          userId: userInfo.id
        }

        const res = await this.$http.post('/api/posts', postData)

        if (res.data.success) {
          this.closeQuickPost()
          uni.hideLoading()
          uni.showToast({ title: '发布成功', icon: 'success' })
          this.refreshPosts()
        } else {
          uni.hideLoading()
          uni.showToast({ title: res.data?.message || '发布失败', icon: 'none' })
        }
      } catch (error) {
        uni.hideLoading()
        console.error('发布失败:', error)
        uni.showToast({ title: '发布失败: ' + (error.message || '请检查网络'), icon: 'none' })
      }
    },

    formatTime(timestamp) {
      if (!timestamp) return '未知时间'
      
      const date = new Date(timestamp)
      const now = new Date()
      const diff = now - date
      
      const minute = 60 * 1000
      const hour = minute * 60
      const day = hour * 24
      
      if (diff < minute) return '刚刚'
      if (diff < hour) return Math.floor(diff / minute) + '分钟前'
      if (diff < day) return Math.floor(diff / hour) + '小时前'
      if (diff < day * 7) return Math.floor(diff / day) + '天前'
      return date.toLocaleDateString()
    }
  }
}
</script>

<style scoped>
.post-page {
  min-height: 100vh;
  background-color: #f8f8f8;
  padding-bottom: 120rpx;
}

.search-section {
  padding: 20rpx 30rpx;
  background: #fff;
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

.community-content {
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

.posts-list {
  display: flex;
  flex-direction: column;
  gap: 30rpx;
}

.post-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
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

.action-item.active .custom-icon {
  filter: drop-shadow(0 0 4rpx #b8d4ff);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx 0;
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
}

.loading-state {
  text-align: center;
  padding: 40rpx;
}

.loading-text {
  font-size: 28rpx;
  color: #999;
}

.load-more {
  text-align: center;
  padding: 40rpx;
}

.load-text {
  font-size: 28rpx;
  color: #b8d4ff;
}

.quick-post-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 30rpx;
}

.modal-content {
  background: #fff;
  border-radius: 20rpx;
  width: 100%;
  max-width: 600rpx;
  max-height: 80vh;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.modal-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
}

.quick-form {
  padding: 30rpx;
}

.quick-title {
  width: 100%;
  height: 80rpx;
  font-size: 28rpx;
  font-weight: 500;
  padding: 0 0 16rpx 0;
  margin-bottom: 20rpx;
  border-bottom: 2rpx solid #f0f0f0;
  box-sizing: border-box;
}

.quick-title::placeholder {
  font-weight: normal;
  color: #ccc;
}

.quick-content {
  width: 100%;
  min-height: 200rpx;
  font-size: 28rpx;
  line-height: 1.6;
  margin-bottom: 20rpx;
}

.char-count {
  font-size: 24rpx;
  color: #999;
  text-align: right;
  display: block;
  margin-bottom: 24rpx;
}

.quick-actions {
  display: flex;
  gap: 20rpx;
  margin-bottom: 24rpx;
}

.action-btn {
  width: 60rpx;
  height: 60rpx;
  background: #f5f5f5;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.quick-images {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  margin-bottom: 30rpx;
}

.quick-image-item {
  position: relative;
  width: 120rpx;
  height: 120rpx;
  border-radius: 12rpx;
  overflow: hidden;
}

.image-preview {
  width: 100%;
  height: 100%;
}

.remove-image {
  position: absolute;
  top: 8rpx;
  right: 8rpx;
  width: 32rpx;
  height: 32rpx;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.quick-submit {
  padding-top: 20rpx;
  border-top: 1rpx solid #f0f0f0;
}

.submit-btn {
  background: #b8d4ff;
  color: #fff;
  border: none;
  border-radius: 40rpx;
  padding: 24rpx;
  font-size: 28rpx;
}

.submit-btn[disabled] {
  background: #ccc;
  color: #999;
}

.custom-icon {
  width: 40rpx;
  height: 40rpx;
}

.large-icon {
  width: 50rpx;
  height: 50rpx;
}

.floating-action-btn {
  position: fixed;
  bottom: 140rpx;
  right: 40rpx;
  z-index: 999;
}

.fab-icon {
  width: 100rpx;
  height: 100rpx;
  background: #b8d4ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 32rpx rgba(142, 172, 255, 0.3);
}
</style>