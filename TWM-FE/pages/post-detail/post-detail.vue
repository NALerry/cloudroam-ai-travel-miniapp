<template>
  <view class="post-detail">
    <!-- 顶部导航栏 -->
    <view class="navbar">
      <image src="/static/icons/general/back.png" class="nav-icon" @tap="goBack"></image>
      <text class="nav-title">帖子详情</text>
      <image src="/static/icons/general/more.png" class="nav-icon"></image>
    </view>

    <!-- 帖子内容区域 -->
    <scroll-view class="post-content" scroll-y :style="{height: scrollViewHeight + 'px'}" @scrolltolower="loadMoreComments">
      <!-- 帖子头部信息 -->
      <view class="post-header">
        <image class="author-avatar" :src="postDetail.author.avatar" mode="aspectFill"></image>
        <view class="author-info">
          <text class="author-name">{{ postDetail.author.name }}</text>
          <text class="post-time">{{ postDetail.createTime }}</text>
        </view>
        <view class="post-location" v-if="postDetail.location">
          <image src="/static/icons/general/gps1.png" class="custom-icon"></image>
          <text>{{ postDetail.location }}</text>
        </view>
      </view>

      <!-- 帖子标题和正文 -->
      <text class="post-title">{{ postDetail.title }}</text>
      <view class="post-body">
        <text class="post-text">{{ postDetail.content }}</text>
        
        <!-- 帖子图片轮播 -->
        <view class="post-images" v-if="postImages.length">
          <swiper 
            class="image-swiper" 
            indicator-dots 
            autoplay 
            circular 
            interval="3000"
            :style="{height: swiperHeight + 'rpx'}"
          >
            <swiper-item 
              v-for="(image, index) in postImages" 
              :key="index"
            >
              <image :src="image" mode="aspectFill" class="detail-image" @tap="previewImage(postImages, index)"></image>
            </swiper-item>
          </swiper>
        </view>
      </view>

      <!-- 互动区域 -->
      <view class="post-actions">
        <!-- 收藏按钮 -->
        <view class="action-item" @tap="toggleCollect">
          <image 
            :src="postDetail.isCollected ? '/static/icons/general/favorite1.png' : '/static/icons/general/favorite.png'" 
            class="custom-icon"
          ></image>
          <text>{{ postDetail.collectCount }}</text>
        </view>
        <!-- 点赞按钮 -->
        <view class="action-item" @tap="toggleLike">
          <image 
            :src="postDetail.isLiked ? '/static/icons/general/like1.png' : '/static/icons/general/like.png'" 
            class="custom-icon"
          ></image>
          <text>{{ postDetail.likeCount }}</text>
        </view>
        <view class="action-item" @tap="showCommentInput">
          <image src="/static/icons/general/comment.png" class="custom-icon"></image>
          <text>{{ postDetail.commentCount }}</text>
        </view>
        <view class="action-item" @tap="sharePost">
          <image src="/static/icons/general/share.png" class="custom-icon"></image>
          <text>分享</text>
        </view>
      </view>

      <!-- 评论列表 -->
      <view class="comments-section">
        <view class="section-header">
          <text class="section-title">评论({{ comments.length }})</text>
          <text class="sort-btn" @tap="toggleSort">{{ sortByTime ? '按热度' : '按时间' }}</text>
        </view>
        
        <view class="comment-list">
          <view 
            class="comment-item" 
            v-for="(comment, index) in comments" 
            :key="comment.id"
          >
            <image class="comment-avatar" :src="comment.author.avatar" mode="aspectFill"></image>
            <view class="comment-content">
              <view class="comment-header">
                <text class="comment-author">{{ comment.author.name }}</text>
                <text class="comment-time">{{ formatTime(comment.createdAt) }}</text>
              </view>
              <text class="comment-text">{{ comment.content }}</text>
              <view class="comment-footer">
                <view class="comment-actions">
                  <text class="action-btn" @tap="replyComment(comment)">回复</text>
                  <text class="action-btn" @tap="toggleCommentLike(comment)">
                    <image 
                      :src="comment.isLiked ? '/static/icons/general/like1.png' : '/static/icons/general/like.png'" 
                      class="small-icon"
                    ></image>
                    {{ comment.likeCount }}
                  </text>
                </view>
              </view>
            </view>
          </view>
        </view>

        <!-- 加载更多 -->
        <view class="load-more" v-if="hasMoreComments && comments.length > 0 && !loadingComments">
          <text class="load-text" @tap="loadMoreComments">加载更多评论</text>
        </view>

        <!-- 空状态 -->
        <view class="empty-state" v-if="comments.length === 0 && !loadingComments">
          <image src="/static/icons/general/comment.png" class="empty-icon"></image>
          <text class="empty-text">暂无评论，快来抢沙发吧～</text>
        </view>

        <!-- 加载状态 -->
        <view class="loading-state" v-if="loadingComments">
          <text class="loading-text">加载中...</text>
        </view>
      </view>
    </scroll-view>

    <!-- 底部评论输入框 -->
    <view class="comment-input-section" v-if="showComment">
      <view class="input-container">
        <input 
          class="comment-input" 
          v-model="commentText" 
          :placeholder="replyTo ? '回复 @' + replyTo.author.name : '写下你的评论...'" 
          :focus="autoFocus"
          maxlength="200"
          @blur="onInputBlur"
        />
        <text class="char-count">{{ commentText.length }}/200</text>
      </view>
      <button class="submit-btn" @tap="submitComment" :disabled="!commentText.trim()">发送</button>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      postId: null,
      showComment: false,
      commentText: '',
      autoFocus: false,
      sortByTime: true,
      scrollViewHeight: 0,
      swiperHeight: 500,
      currentCommentPage: 1,
      commentPageSize: 10,
      hasMoreComments: true,
      loadingComments: false,
      replyTo: null,
      baseUrl: 'http://localhost:8080',
      
      postDetail: {
        id: 0,
        title: '',
        content: '',
        images: [],
        author: {
          name: '',
          avatar: ''
        },
        location: '',
        createTime: '',
        likeCount: 0,
        commentCount: 0,
        isLiked: false,
        collectCount: 0,
        isCollected: false
      },
      comments: []
    }
  },
  computed: {
    postImages() {
      if (!this.postDetail.images) return []
      if (Array.isArray(this.postDetail.images)) {
        return this.postDetail.images.map(img => this.getFullImageUrl(img))
      }
      if (typeof this.postDetail.images === 'string') {
        try {
          const parsed = JSON.parse(this.postDetail.images)
          if (Array.isArray(parsed)) {
            return parsed.map(img => this.getFullImageUrl(img))
          }
          return this.postDetail.images.split(',').filter(u => u && u.trim()).map(img => this.getFullImageUrl(img.trim()))
        } catch (e) {
          return this.postDetail.images.split(',').filter(u => u && u.trim()).map(img => this.getFullImageUrl(img.trim()))
        }
      }
      return []
    }
  },
  onLoad(options) {
    console.log('接收到的参数:', options)
    
    this.postId = parseInt(options.id) || 1
    this.showComment = options.mode === 'comment' || false
    this.autoFocus = options.mode === 'comment'
    
    this.calculateScrollHeight()
    this.loadPostDetail()
    this.loadComments()
    
    uni.$on('collectionStatusChanged', this.handleCollectionStatusChanged)
    uni.$on('likeStatusChanged', this.handleLikeStatusChanged)
    uni.$on('postUpdated', this.handlePostUpdated)
    
    if (this.showComment) {
      setTimeout(() => {
        this.autoFocus = true
      }, 500)
    }
  },
  onReady() {
    this.calculateScrollHeight()
  },
  onShow() {
    this.calculateScrollHeight()
    this.checkCollectionStatus()
  },
  onUnload() {
    uni.$off('collectionStatusChanged', this.handleCollectionStatusChanged)
    uni.$off('likeStatusChanged', this.handleLikeStatusChanged)
    uni.$off('postUpdated', this.handlePostUpdated)
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
      console.log('详情页收到帖子更新事件:', data)
      
      if (data.action === 'delete') {
        if (this.postDetail.id === data.postId) {
          uni.showModal({
            title: '提示',
            content: '该帖子已被删除',
            success: () => {
              uni.navigateBack()
            }
          })
        }
      } else if (this.postDetail.id === data.postId) {
        this.loadPostDetail()
        uni.showToast({ title: '内容已更新', icon: 'success' })
      }
    },

    async checkCollectionStatus() {
      try {
        const userInfo = uni.getStorageSync('user_info')
        if (userInfo && userInfo.id) {
          const collectionRes = await this.$http.get(`/api/collections/user/${userInfo.id}/check/${this.postId}`)
          const isCollected = collectionRes.data.collected
          
          if (this.postDetail.isCollected !== isCollected) {
            this.postDetail.isCollected = isCollected
            if (isCollected) {
              this.postDetail.collectCount = Math.max(1, this.postDetail.collectCount)
            } else {
              this.postDetail.collectCount = Math.max(0, this.postDetail.collectCount - 1)
            }
            console.log('详情页重新检查收藏状态:', isCollected)
            this.$forceUpdate()
          }
        }
      } catch (error) {
        console.error('检查收藏状态失败:', error)
      }
    },
    
    calculateScrollHeight() {
      const systemInfo = uni.getSystemInfoSync()
      const windowHeight = systemInfo.windowHeight
      const statusBarHeight = systemInfo.statusBarHeight || 0
      const navigationBarHeight = 44
      
      let availableHeight = windowHeight - statusBarHeight - navigationBarHeight
      
      if (this.showComment) {
        availableHeight -= 100
      }
      
      this.scrollViewHeight = availableHeight
      
      const screenWidth = systemInfo.screenWidth || systemInfo.windowWidth
      const calculatedHeight = (screenWidth * 4 / 3) * (750 / systemInfo.windowWidth)
      this.swiperHeight = Math.min(calculatedHeight, 800)
    },
    
    onInputBlur() {
      setTimeout(() => {
        this.calculateScrollHeight()
      }, 300)
    },

    getAvatarUrl(avatar) {
      if (!avatar) {
        return '/static/images/default-avatar.png'
      }
      if (avatar.startsWith('http') || avatar.startsWith('https')) {
        return avatar
      }
      if (avatar.startsWith('/uploads/')) {
        return this.baseUrl + avatar
      }
      return avatar
    },
  
    handleCollectionStatusChanged(data) {
      if (data.postId === this.postDetail.id) {
        this.postDetail.isCollected = data.isCollected
        this.postDetail.collectCount = data.collectCount
        this.$forceUpdate()
      }
    },

    handleLikeStatusChanged(data) {
      if (data.postId === this.postDetail.id) {
        this.postDetail.isLiked = data.isLiked
        this.postDetail.likeCount = data.likeCount
        this.$forceUpdate()
      }
    },

    async toggleCollect() {
      try {
        const userInfo = uni.getStorageSync('user_info')
        if (!userInfo || !userInfo.id) {
          uni.showToast({ title: '请先登录', icon: 'none' })
          uni.navigateTo({ url: '/pages/login/login' })
          return
        }

        const wasCollected = this.postDetail.isCollected
        const oldCount = this.postDetail.collectCount || 0
        
        this.postDetail.isCollected = !wasCollected
        this.postDetail.collectCount = wasCollected ? Math.max(0, oldCount - 1) : Math.max(1, oldCount + 1)

        if (wasCollected) {
          const result = await this.$http.delete(`/api/collections/user/${userInfo.id}/post/${this.postDetail.id}`)
          if (result.data.success) {
            uni.showToast({ title: '已取消收藏', icon: 'success' })
            if (this.postDetail.collectCount < 0) {
              this.postDetail.collectCount = 0
            }
          } else {
            this.postDetail.isCollected = wasCollected
            this.postDetail.collectCount = oldCount
            throw new Error('取消收藏失败')
          }
        } else {
          const result = await this.$http.post('/api/collections', {
            userId: userInfo.id,
            postId: this.postDetail.id
          })
          if (result.data.success) {
            uni.showToast({ title: '收藏成功', icon: 'success' })
          } else {
            this.postDetail.isCollected = wasCollected
            this.postDetail.collectCount = oldCount
            throw new Error('收藏失败')
          }
        }
        
        this.$forceUpdate()
        
        uni.$emit('collectionStatusChanged', {
          postId: this.postDetail.id,
          isCollected: this.postDetail.isCollected,
          collectCount: this.postDetail.collectCount
        })
        
      } catch (error) {
        console.error('收藏操作失败:', error)
        uni.showToast({ title: '操作失败，请重试', icon: 'none' })
      }
    },
    
    async toggleLike() {
      try {
        const userInfo = uni.getStorageSync('user_info')
        if (!userInfo || !userInfo.id) {
          uni.showToast({ title: '请先登录', icon: 'none' })
          uni.navigateTo({ url: '/pages/login/login' })
          return
        }

        const wasLiked = this.postDetail.isLiked
        const oldCount = this.postDetail.likeCount || 0
        
        this.postDetail.isLiked = !wasLiked
        this.postDetail.likeCount = wasLiked ? Math.max(0, oldCount - 1) : Math.max(1, oldCount + 1)

        if (wasLiked) {
          await this.$http.delete(`/api/likes/user/${userInfo.id}/post/${this.postDetail.id}`)
          uni.showToast({ title: '已取消点赞', icon: 'success' })
          if (this.postDetail.likeCount < 0) {
            this.postDetail.likeCount = 0
          }
        } else {
          await this.$http.post('/api/likes', {
            userId: userInfo.id,
            postId: this.postDetail.id
          })
          uni.showToast({ title: '点赞成功', icon: 'success' })
        }
        
        this.$forceUpdate()
        
        uni.$emit('likeStatusChanged', {
          postId: this.postDetail.id,
          isLiked: this.postDetail.isLiked,
          likeCount: this.postDetail.likeCount
        })
        
      } catch (error) {
        console.error('点赞操作失败:', error)
        uni.showToast({ title: '操作失败', icon: 'none' })
      }
    },

    async loadPostDetail() {
      console.log('加载帖子详情，ID:', this.postId)
      
      try {
        const res = await this.$http.get(`/api/posts/${this.postId}`)
        if (res.data.success) {
          const postData = res.data.data
          console.log('帖子数据:', postData)
          
          // 解析图片URL
          let images = []
          if (postData.imageUrls) {
            if (Array.isArray(postData.imageUrls)) {
              images = postData.imageUrls
            } else if (typeof postData.imageUrls === 'string') {
              try {
                const parsed = JSON.parse(postData.imageUrls)
                if (Array.isArray(parsed)) {
                  images = parsed
                } else {
                  images = postData.imageUrls.split(',').filter(url => url && url.trim())
                }
              } catch (e) {
                images = postData.imageUrls.split(',').filter(url => url && url.trim())
              }
            }
          }
          
          const userInfo = uni.getStorageSync('user_info')
          let isCollected = false
          let isLiked = false
          
          if (userInfo && userInfo.id) {
            try {
              const collectionRes = await this.$http.get(`/api/collections/user/${userInfo.id}/check/${this.postId}`)
              isCollected = collectionRes.data.collected
            } catch (error) {
              console.error('检查收藏状态失败:', error)
            }
            
            try {
              const likeRes = await this.$http.get(`/api/likes/user/${userInfo.id}/check/${this.postId}`)
              isLiked = likeRes.data.liked
            } catch (error) {
              console.error('检查点赞状态失败:', error)
            }
          }
          
          this.postDetail = {
            id: postData.id,
            title: postData.title,
            content: postData.content,
            images: images,
            author: {
              name: postData.author?.nickname || postData.author?.username || '匿名用户',
              avatar: this.getAvatarUrl(postData.author?.avatar)
            },
            location: postData.location,
            createTime: this.formatTime(postData.createdAt),
            likeCount: isLiked ? Math.max(1, postData.likeCount || 0) : (postData.likeCount || 0),
            commentCount: postData.commentCount || 0,
            collectCount: isCollected ? Math.max(1, postData.collectCount || 0) : (postData.collectCount || 0),
            isLiked: isLiked,
            isCollected: isCollected
          }
          
          console.log('帖子详情加载成功，图片数量:', this.postDetail.images.length)
          
          // ============ 关键修改：添加浏览历史记录 ============
          await this.addToHistory()
          // =================================================
        }
      } catch (error) {
        console.error('加载帖子详情失败:', error)
        this.postDetail = {
          id: this.postId,
          title: '未知帖子',
          content: '这个帖子不存在或已被删除。',
          images: [],
          author: {
            name: '未知用户',
            avatar: '/static/images/default-avatar.png'
          },
          location: '',
          createTime: '未知时间',
          likeCount: 0,
          commentCount: 0,
          collectCount: 0,
          isLiked: false,
          isCollected: false
        }
      }
    },
    
    // ============ 新增方法：添加浏览历史记录 ============
    async addToHistory() {
      try {
        const userInfo = uni.getStorageSync('user_info')
        // 未登录用户不记录浏览历史
        if (!userInfo || !userInfo.id) {
          console.log('用户未登录，不记录浏览历史')
          return
        }
        
        const token = uni.getStorageSync('user_token')
        
        // 构建历史记录数据 - 使用时间戳（毫秒数）
        const historyData = {
          userId: userInfo.id,
          postId: this.postDetail.id,
          browseTime: Date.now()  // 使用时间戳，后端期望 Long 类型
        }
        
        console.log('添加浏览历史:', historyData)
        
        // 调用后端API添加浏览记录
        const res = await new Promise((resolve, reject) => {
          uni.request({
            url: `http://localhost:8080/api/history`,
            method: 'POST',
            header: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            data: historyData,
            success: (res) => {
              resolve(res)
            },
            fail: (err) => {
              reject(err)
            }
          })
        })
        
        if (res.statusCode === 200 && res.data && res.data.success) {
          console.log('浏览历史记录成功:', res.data)
        } else {
          console.log('浏览历史记录失败:', res.data?.message || '未知错误')
        }
      } catch (error) {
        console.error('添加浏览历史失败:', error)
        // 静默失败，不影响用户体验
      }
    },
    // ====================================================
    
    async loadComments() {
      if (this.loadingComments) return
      
      this.loadingComments = true
      
      try {
        const res = await this.$http.get(`/api/comments/post/${this.postId}`, {
          page: this.currentCommentPage,
          size: this.commentPageSize
        })
        
        if (res.data.success) {
          const commentsData = res.data.data
          
          const commentsWithUserInfo = await Promise.all(
            commentsData.map(async (comment) => {
              let authorInfo = {
                name: '匿名用户',
                avatar: '/static/images/default-avatar.png'
              }
              
              if (comment.userId) {
                try {
                  const userRes = await this.$http.get(`/api/users/${comment.userId}`)
                  if (userRes.data.success) {
                    const user = userRes.data.data
                    authorInfo = {
                      name: user.nickname || user.username || '匿名用户',
                      avatar: this.getAvatarUrl(user.avatar)
                    }
                  }
                } catch (error) {
                  console.error('加载评论用户信息失败:', error)
                }
              }
              
              return {
                ...comment,
                author: authorInfo,
                isLiked: false,
                likeCount: comment.likeCount || 0
              }
            })
          )
          
          if (this.currentCommentPage === 1) {
            this.comments = commentsWithUserInfo
          } else {
            this.comments = [...this.comments, ...commentsWithUserInfo]
          }
          
          this.hasMoreComments = res.data.hasNext
        }
      } catch (error) {
        console.error('加载评论失败:', error)
        uni.showToast({ title: '加载评论失败', icon: 'none' })
      } finally {
        this.loadingComments = false
      }
    },
    
    loadMoreComments() {
      if (!this.hasMoreComments || this.loadingComments) {
        return
      }
      
      this.currentCommentPage++
      this.loadComments()
    },
    
    goBack() {
      uni.navigateBack()
    },
    
    showCommentInput() {
      this.showComment = true
      this.replyTo = null
      this.autoFocus = true
      this.calculateScrollHeight()
    },
    
    toggleSort() {
      this.sortByTime = !this.sortByTime
      this.comments.sort((a, b) => {
        if (this.sortByTime) {
          return new Date(b.createdAt) - new Date(a.createdAt)
        } else {
          return b.likeCount - a.likeCount
        }
      })
      
      uni.showToast({
        title: this.sortByTime ? '按时间排序' : '按热度排序',
        icon: 'none'
      })
    },
    
    previewImage(images, currentIndex) {
      uni.previewImage({
        current: currentIndex,
        urls: images
      })
    },
    
    sharePost() {
      uni.showActionSheet({
        itemList: ['分享给好友', '分享到朋友圈', '复制链接'],
        success: (res) => {
          const methods = ['好友', '朋友圈', '复制链接']
          uni.showToast({
            title: `已分享到${methods[res.tapIndex]}`,
            icon: 'success'
          })
        }
      })
    },
    
    replyComment(comment) {
      this.replyTo = comment
      this.commentText = `回复 @${comment.author.name}: `
      this.showComment = true
      this.autoFocus = true
      this.calculateScrollHeight()
    },
    
    async toggleCommentLike(comment) {
      try {
        const userInfo = uni.getStorageSync('user_info')
        if (!userInfo || !userInfo.id) {
          uni.showToast({ title: '请先登录', icon: 'none' })
          uni.navigateTo({ url: '/pages/login/login' })
          return
        }

        if (comment.isLiked) {
          await this.$http.post(`/api/comments/${comment.id}/unlike`, {
            userId: userInfo.id
          })
          comment.isLiked = false
          comment.likeCount = Math.max(0, comment.likeCount - 1)
        } else {
          await this.$http.post(`/api/comments/${comment.id}/like`, {
            userId: userInfo.id
          })
          comment.isLiked = true
          comment.likeCount = Math.max(1, comment.likeCount + 1)
        }
      } catch (error) {
        console.error('点赞评论操作失败:', error)
        uni.showToast({ title: '操作失败', icon: 'none' })
      }
    },
    
    async submitComment() {
      if (!this.commentText.trim()) {
        uni.showToast({ title: '请输入评论内容', icon: 'none' })
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
        const commentData = {
          content: this.commentText,
          userId: userInfo.id,
          postId: this.postId
        }

        if (this.replyTo) {
          commentData.parentId = this.replyTo.id
        }

        const res = await this.$http.post('/api/comments', commentData)

        if (res.data.success) {
          this.commentText = ''
          this.showComment = false
          this.autoFocus = false
          this.replyTo = null
          
          this.currentCommentPage = 1
          await this.loadComments()
          
          this.postDetail.commentCount += 1
          
          uni.hideLoading()
          uni.showToast({ title: '评论成功', icon: 'success' })
          
          this.calculateScrollHeight()
        }
      } catch (error) {
        uni.hideLoading()
        console.error('发布评论失败:', error)
        uni.showToast({ title: '评论发布失败', icon: 'none' })
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
      
      if (diff < minute) {
        return '刚刚'
      } else if (diff < hour) {
        return Math.floor(diff / minute) + '分钟前'
      } else if (diff < day) {
        return Math.floor(diff / hour) + '小时前'
      } else if (diff < day * 7) {
        return Math.floor(diff / day) + '天前'
      } else {
        return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
      }
    }
  }
}
</script>

<style scoped>
.post-detail {
  min-height: 100vh;
  background-color: #f8f8f8;
  display: flex;
  flex-direction: column;
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
  flex-shrink: 0;
  height: 88rpx;
  box-sizing: border-box;
}

.nav-icon {
  width: 40rpx;
  height: 40rpx;
  flex-shrink: 0;
}

.nav-title {
  font-size: 36rpx;
  font-weight: 500;
  color: #333;
  flex: 1;
  text-align: center;
}

.post-content {
  flex: 1;
  padding: 30rpx;
  box-sizing: border-box;
}

.post-header {
  display: flex;
  align-items: flex-start;
  margin-bottom: 30rpx;
  flex-wrap: wrap;
}

.author-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 40rpx;
  margin-right: 20rpx;
  flex-shrink: 0;
}

.author-info {
  flex: 1;
  min-width: 0;
}

.author-name {
  font-size: 32rpx;
  font-weight: 500;
  color: #333;
  display: block;
  margin-bottom: 8rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.post-time {
  font-size: 24rpx;
  color: #999;
  display: block;
}

.post-location {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 24rpx;
  color: #999;
  margin-top: 8rpx;
  width: 100%;
}

.post-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
  display: block;
  margin-bottom: 24rpx;
  line-height: 1.4;
  word-break: break-word;
}

.post-body {
  margin-bottom: 40rpx;
}

.post-text {
  font-size: 28rpx;
  color: #666;
  line-height: 1.7;
  margin-bottom: 30rpx;
  word-break: break-word;
}

.detail-image {
  width: 100%;
  height: 100%;
  border-radius: 16rpx;
  object-fit: cover;
}

.image-swiper {
  width: 100%;
  border-radius: 16rpx;
  overflow: hidden;
  margin-bottom: 30rpx;
  background-color: #f5f5f5;
}

.post-actions {
  display: flex;
  justify-content: space-around;
  align-items: center;
  height: 120rpx;
  background: #fff;
  border-radius: 16rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
  flex-shrink: 0;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  color: #999;
  flex: 1;
}

.custom-icon {
  width: 40rpx;
  height: 40rpx;
  margin-bottom: 8rpx;
}

.small-icon {
  width: 24rpx;
  height: 24rpx;
  margin-right: 8rpx;
}

.comments-section {
  margin-top: 40rpx;
  flex: 1;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
  padding-bottom: 20rpx;
  border-bottom: 1rpx solid #eee;
  flex-shrink: 0;
}

.section-title {
  font-size: 32rpx;
  font-weight: 500;
  color: #333;
}

.sort-btn {
  font-size: 26rpx;
  color: #999;
  padding: 8rpx 16rpx;
  background: #f5f5f5;
  border-radius: 20rpx;
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 30rpx;
}

.comment-item {
  display: flex;
  gap: 20rpx;
  background: #fff;
  padding: 30rpx;
  border-radius: 16rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
  flex-shrink: 0;
}

.comment-avatar {
  width: 64rpx;
  height: 64rpx;
  border-radius: 32rpx;
  flex-shrink: 0;
}

.comment-content {
  flex: 1;
  min-width: 0;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
  flex-wrap: wrap;
}

.comment-author {
  font-size: 28rpx;
  font-weight: 500;
  color: #333;
  margin-right: 20rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.comment-time {
  font-size: 22rpx;
  color: #999;
  flex-shrink: 0;
}

.comment-text {
  font-size: 28rpx;
  color: #666;
  line-height: 1.5;
  margin-bottom: 20rpx;
  display: block;
  word-break: break-word;
}

.comment-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.comment-actions {
  display: flex;
  gap: 20rpx;
}

.action-btn {
  display: flex;
  align-items: center;
  font-size: 24rpx;
  color: #999;
  padding: 8rpx 16rpx;
  background: #f5f5f5;
  border-radius: 6rpx;
  flex-shrink: 0;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx 0;
  text-align: center;
  flex: 1;
}

.empty-icon {
  width: 120rpx;
  height: 120rpx;
  opacity: 0.5;
  margin-bottom: 30rpx;
}

.empty-text {
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

.loading-state {
  text-align: center;
  padding: 40rpx;
}

.loading-text {
  font-size: 28rpx;
  color: #999;
}

.comment-input-section {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: flex-end;
  padding: 20rpx 30rpx;
  background: #fff;
  border-top: 1rpx solid #eee;
  z-index: 10;
  box-shadow: 0 -2rpx 12rpx rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.input-container {
  flex: 1;
  position: relative;
  margin-right: 20rpx;
}

.comment-input {
  width: 100%;
  height: 80rpx;
  background: #f8f8f8;
  border-radius: 40rpx;
  padding: 0 30rpx;
  font-size: 28rpx;
  padding-right: 120rpx;
  box-sizing: border-box;
}

.char-count {
  position: absolute;
  right: 30rpx;
  top: 50%;
  transform: translateY(-50%);
  font-size: 22rpx;
  color: #999;
}

.submit-btn {
  background: #b8d4ff;
  color: #fff;
  border-radius: 40rpx;
  padding: 0 40rpx;
  height: 80rpx;
  line-height: 80rpx;
  font-size: 28rpx;
  border: none;
  flex-shrink: 0;
  min-width: 120rpx;
}

.submit-btn[disabled] {
  background: #ccc;
  color: #999;
}

@media (max-width: 750rpx) {
  .post-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .author-avatar {
    margin-bottom: 20rpx;
  }
  
  .post-location {
    margin-top: 15rpx;
  }
  
  .comment-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .comment-time {
    margin-top: 8rpx;
  }
}

@media (min-width: 751rpx) and (max-width: 1200rpx) {
  .post-content {
    padding: 40rpx;
    max-width: 1200rpx;
    margin: 0 auto;
    width: 100%;
  }
  
  .comment-item {
    padding: 40rpx;
  }
}

@media (min-width: 1201rpx) {
  .post-content {
    padding: 50rpx;
    max-width: 1200rpx;
    margin: 0 auto;
    width: 100%;
  }
  
  .comment-item {
    padding: 50rpx;
  }
}
</style>