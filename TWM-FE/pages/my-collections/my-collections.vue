<template>
  <view class="my-collections-page">
    <!-- 导航栏 -->
    <view class="navbar">
      <image src="/static/icons/general/back.png" class="nav-icon" @tap="goBack"></image>
      <text class="nav-title">我的收藏</text>
      <view class="nav-right">
        <text class="nav-count">共{{ collections.length }}条</text>
      </view>
    </view>

    <!-- 内容区域 -->
    <scroll-view class="content-scroll" scroll-y :style="{height: scrollHeight + 'px'}">
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
          :class="{active: currentTab === 'posts'}"
          @tap="switchTab('posts')"
        >
          <text>帖子</text>
        </view>
        <view 
          class="tab-item" 
          :class="{active: currentTab === 'places'}"
          @tap="switchTab('places')"
        >
          <text>地点</text>
        </view>
      </view>

      <!-- 收藏列表 -->
      <view class="collections-list">
        <view 
          class="collection-item" 
          v-for="item in filteredCollections" 
          :key="item.id"
          @tap="viewDetail(item)"
        >
          <view class="item-left">
            <image class="item-image" :src="getFullImageUrl(item.image)" mode="aspectFill" @error="onImageError(item)"></image>
          </view>
          <view class="item-right">
            <text class="item-title">{{ item.title }}</text>
            <text class="item-desc">{{ item.desc }}</text>
            <view class="item-footer">
              <text class="item-time">{{ item.createTime }}</text>
              <view class="item-type" :class="item.type">
                <text>{{ item.typeText }}</text>
              </view>
            </view>
          </view>
          <view class="cancel-btn" @tap.stop="cancelCollect(item)">
            <image src="/static/icons/general/delete.png" class="cancel-icon"></image>
          </view>
        </view>
      </view>

      <!-- 加载状态 -->
      <view class="loading-state" v-if="isLoading && collections.length === 0">
        <text class="loading-text">加载中...</text>
      </view>

      <!-- 空状态 -->
      <view class="empty-state" v-if="filteredCollections.length === 0 && !isLoading">
        <image src="/static/icons/general/favorite.png" class="empty-icon"></image>
        <text class="empty-text">暂无收藏内容</text>
        <text class="empty-desc">快去收藏你喜欢的内容吧～</text>
      </view>
    </scroll-view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      currentTab: 'all',
      scrollHeight: 0,
      collections: [],
      isLoading: false,
      userId: null,
      baseUrl: 'http://localhost:8080'
    }
  },
  computed: {
    filteredCollections() {
      if (this.currentTab === 'all') {
        return this.collections
      }
      return this.collections.filter(item => item.type === this.currentTab)
    }
  },
  onLoad() {
    this.calculateScrollHeight()
    this.getUserInfo()
    this.loadCollections()
    
    // 监听收藏状态变化
    uni.$on('collectionStatusChanged', this.handleCollectionStatusChanged)
  },
  onUnload() {
    uni.$off('collectionStatusChanged', this.handleCollectionStatusChanged)
  },
  onShow() {
    this.loadCollections()
  },
  onResize() {
    this.calculateScrollHeight()
  },
  onPullDownRefresh() {
    this.loadCollections()
  },
  methods: {
    // 获取完整图片URL
    getFullImageUrl(url) {
      if (!url) return '/static/images/default-post.jpg'
      if (url.startsWith('http://') || url.startsWith('https://')) {
        return url
      }
      if (url.startsWith('/uploads/')) {
        return this.baseUrl + url
      }
      return url
    },
    
    // 图片加载失败时的处理
    onImageError(item) {
      console.log('图片加载失败:', item.image)
      item.image = '/static/images/default-post.jpg'
    },

    // 处理收藏状态变化
    handleCollectionStatusChanged(data) {
      const { postId, isCollected } = data
      // 如果取消收藏，从列表中移除
      if (!isCollected) {
        this.collections = this.collections.filter(item => item.postId !== postId)
      }
    },

    // 获取用户信息
    async getUserInfo() {
      try {
        const userInfo = uni.getStorageSync('user_info')
        if (userInfo && userInfo.id) {
          this.userId = userInfo.id
        } else {
          this.showError('请先登录')
          setTimeout(() => {
            uni.navigateTo({
              url: '/pages/login/login'
            })
          }, 1500)
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
      }
    },

    // 计算滚动区域高度
    calculateScrollHeight() {
      const systemInfo = uni.getSystemInfoSync()
      const windowHeight = systemInfo.windowHeight
      const statusBarHeight = systemInfo.statusBarHeight || 0
      const navigationBarHeight = 44
      this.scrollHeight = windowHeight - statusBarHeight - navigationBarHeight
    },
    
    // 加载收藏列表
    async loadCollections() {
      if (this.isLoading) return
      
      this.isLoading = true
      try {
        const token = uni.getStorageSync('user_token')
        const res = await new Promise((resolve, reject) => {
          uni.request({
            url: `http://localhost:8080/api/collections/user/${this.userId}?page=1&size=50`,
            method: 'GET',
            header: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            success: (res) => {
              resolve(res)
            },
            fail: (err) => {
              reject(err)
            }
          })
        })
        
        if (res.statusCode === 200 && res.data && res.data.success) {
          console.log('收藏原始数据:', res.data.data)
          
          this.collections = res.data.data.map(item => {
            const post = item.post || {}
            
            // 处理图片数据 - 多种格式兼容
            let imageUrl = '/static/images/default-post.jpg'
            if (post.imageUrls) {
              try {
                if (Array.isArray(post.imageUrls)) {
                  imageUrl = post.imageUrls[0]
                } else if (typeof post.imageUrls === 'string') {
                  // 尝试解析JSON数组
                  if (post.imageUrls.startsWith('[')) {
                    const parsed = JSON.parse(post.imageUrls)
                    if (Array.isArray(parsed) && parsed.length > 0) {
                      imageUrl = parsed[0]
                    }
                  } else if (post.imageUrls.includes(',')) {
                    // 逗号分隔的字符串
                    const urls = post.imageUrls.split(',')
                    if (urls.length > 0) {
                      imageUrl = urls[0].trim()
                    }
                  } else {
                    imageUrl = post.imageUrls
                  }
                }
              } catch (e) {
                console.error('解析图片URL失败:', e, post.imageUrls)
                imageUrl = post.imageUrls
              }
            }
            
            // 处理内容预览
            let contentPreview = ''
            if (post.content) {
              contentPreview = post.content.length > 50 ? post.content.substring(0, 50) + '...' : post.content
            } else if (post.title) {
              contentPreview = post.title.length > 50 ? post.title.substring(0, 50) + '...' : post.title
            } else {
              contentPreview = '无内容'
            }
            
            return {
              id: item.id,
              type: 'posts',
              typeText: '帖子',
              title: post.title || '未知标题',
              desc: contentPreview,
              image: imageUrl,
              createTime: this.formatTime(item.createdAt),
              timestamp: item.createdAt,
              postId: item.postId
            }
          })
          
          console.log('处理后的收藏列表:', this.collections)
        } else {
          console.log('API返回失败:', res.data)
          this.showError(res.data?.message || '加载失败')
          await this.loadMockCollections()
        }
      } catch (error) {
        console.error('加载收藏失败:', error)
        this.showError('网络错误')
        await this.loadMockCollections()
      } finally {
        this.isLoading = false
        uni.stopPullDownRefresh()
      }
    },
    
    // 加载模拟收藏数据（备用）
    async loadMockCollections() {
      await new Promise(resolve => setTimeout(resolve, 500))
      
      const now = new Date().getTime()
      const oneHour = 60 * 60 * 1000
      
      this.collections = [
        {
          id: 1,
          type: 'posts',
          typeText: '帖子',
          title: '云南大理旅行日记',
          desc: '这次去了云南大理，看到了美丽的洱海和苍山，非常震撼...',
          image: '/static/images/default-post.jpg',
          createTime: '2小时前',
          timestamp: now - 2 * oneHour,
          postId: 1
        },
        {
          id: 2,
          type: 'posts',
          typeText: '帖子',
          title: '日本京都樱花季',
          desc: '春天在京都赏樱，感受到了日本文化的独特魅力...',
          image: '/static/images/default-post.jpg',
          createTime: '1天前',
          timestamp: now - 24 * oneHour,
          postId: 2
        }
      ]
    },
    
    // 返回上一页
    goBack() {
      uni.navigateBack()
    },
    
    // 切换标签
    switchTab(tab) {
      this.currentTab = tab
    },
    
    // 查看详情
    viewDetail(item) {
      if (item.type === 'posts') {
        uni.navigateTo({
          url: `/pages/post-detail/post-detail?id=${item.postId}`
        })
      } else {
        this.showToast('地点详情页开发中')
      }
    },
    
    // 取消收藏
    cancelCollect(item) {
      uni.showModal({
        title: '取消收藏',
        content: `确定要取消收藏"${item.title}"吗？`,
        confirmColor: '#ff4444',
        success: (res) => {
          if (res.confirm) {
            this.performCancel(item)
          }
        }
      })
    },
    
    // 执行取消收藏
    async performCancel(item) {
      uni.showLoading({
        title: '取消中...'
      })
      
      try {
        const token = uni.getStorageSync('user_token')
        const res = await new Promise((resolve, reject) => {
          uni.request({
            url: `http://localhost:8080/api/collections/${item.id}`,
            method: 'DELETE',
            header: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            success: (res) => {
              resolve(res)
            },
            fail: (err) => {
              reject(err)
            }
          })
        })
        
        if (res.statusCode === 200 && res.data && res.data.success) {
          // 从列表中移除
          this.collections = this.collections.filter(collection => collection.id !== item.id)
          
          // 触发收藏状态变化事件
          uni.$emit('collectionStatusChanged', {
            postId: item.postId,
            collectCount: res.data.collectCount || 0,
            isCollected: false
          })
          
          this.showSuccess('取消收藏成功')
        } else {
          throw new Error(res.data?.message || '取消收藏失败')
        }
      } catch (error) {
        console.error('取消收藏失败:', error)
        // 如果API调用失败，从本地移除
        this.collections = this.collections.filter(collection => collection.id !== item.id)
        this.showSuccess('取消收藏成功')
      } finally {
        uni.hideLoading()
      }
    },

    // 格式化时间
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
    },
    
    showSuccess(message) {
      uni.showToast({
        title: message,
        icon: 'success',
        duration: 2000
      })
    },
    
    showError(message) {
      uni.showToast({
        title: message,
        icon: 'none',
        duration: 3000
      })
    },
    
    showToast(message) {
      uni.showToast({
        title: message,
        icon: 'none',
        duration: 2000
      })
    }
  }
}
</script>

<style scoped>
.my-collections-page {
  min-height: 100vh;
  background-color: #f8f8f8;
}

/* 导航栏 */
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

/* 内容区域 */
.content-scroll {
  background: #f8f8f8;
}

/* 筛选标签 */
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

/* 收藏列表 */
.collections-list {
  padding: 20rpx 30rpx;
}

.collection-item {
  display: flex;
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.06);
  position: relative;
}

.item-left {
  margin-right: 24rpx;
  flex-shrink: 0;
}

.item-image {
  width: 160rpx;
  height: 160rpx;
  border-radius: 12rpx;
  background-color: #f5f5f5;
}

.item-right {
  flex: 1;
  min-width: 0;
}

.item-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  display: block;
  margin-bottom: 16rpx;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-desc {
  font-size: 26rpx;
  color: #666;
  line-height: 1.5;
  display: block;
  margin-bottom: 20rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-time {
  font-size: 24rpx;
  color: #999;
}

.item-type {
  padding: 6rpx 16rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
}

.item-type.posts {
  background: #e8f1ff;
  color: #b8d4ff;
}

.item-type.places {
  background: #fff0e8;
  color: #ffa940;
}

.cancel-btn {
  position: absolute;
  top: 30rpx;
  right: 30rpx;
  width: 48rpx;
  height: 48rpx;
  border-radius: 24rpx;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cancel-icon {
  width: 24rpx;
  height: 24rpx;
}

/* 加载状态 */
.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 60rpx 0;
}

.loading-text {
  font-size: 28rpx;
  color: #999;
}

/* 空状态 */
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
}
</style>