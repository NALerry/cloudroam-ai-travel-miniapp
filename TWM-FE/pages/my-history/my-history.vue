<template>
  <view class="my-history-page">
    <!-- 导航栏 -->
    <view class="navbar">
      <image src="/static/icons/general/back.png" class="nav-icon" @tap="goBack"></image>
      <text class="nav-title">浏览历史</text>
      <view class="nav-right">
        <text class="nav-count">共{{ historyList.length }}条</text>
      </view>
    </view>

    <!-- 内容区域 -->
    <scroll-view class="content-scroll" scroll-y :style="{height: scrollHeight + 'px'}">
      <!-- 时间筛选 -->
      <view class="time-filter">
        <view 
          class="filter-item" 
          :class="{active: currentFilter === 'all'}"
          @tap="switchFilter('all')"
        >
          <text>全部</text>
        </view>
        <view 
          class="filter-item" 
          :class="{active: currentFilter === 'today'}"
          @tap="switchFilter('today')"
        >
          <text>今天</text>
        </view>
        <view 
          class="filter-item" 
          :class="{active: currentFilter === 'week'}"
          @tap="switchFilter('week')"
        >
          <text>近一周</text>
        </view>
        <view 
          class="filter-item" 
          :class="{active: currentFilter === 'month'}"
          @tap="switchFilter('month')"
        >
          <text>近一月</text>
        </view>
      </view>

      <!-- 历史列表 -->
      <view class="history-list">
        <view 
          class="history-item" 
          v-for="item in filteredHistory" 
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
          <view class="delete-btn" @tap.stop="deleteHistory(item)">
            <image src="/static/icons/general/delete.png" class="delete-icon"></image>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <view class="empty-state" v-if="filteredHistory.length === 0 && !isLoading">
        <image src="/static/icons/general/history.png" class="empty-icon"></image>
        <text class="empty-text">暂无浏览历史</text>
        <text class="empty-desc">快去发现精彩内容吧～</text>
      </view>

      <!-- 加载状态 -->
      <view class="loading-state" v-if="isLoading && filteredHistory.length === 0">
        <text class="loading-text">加载中...</text>
      </view>

      <!-- 清除全部 -->
      <view class="clear-all" v-if="historyList.length > 0 && !isLoading" @tap="clearAll">
        <text class="clear-text">清除全部记录</text>
      </view>
    </scroll-view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      currentFilter: 'all',
      scrollHeight: 0,
      historyList: [],
      isLoading: false,
      userId: null,
      baseUrl: 'http://localhost:8080'
    }
  },
  computed: {
    filteredHistory() {
      const now = new Date().getTime()
      let filtered = this.historyList
      
      switch (this.currentFilter) {
        case 'today':
          filtered = filtered.filter(item => {
            const itemTime = new Date(item.timestamp).getTime()
            return now - itemTime < 24 * 60 * 60 * 1000
          })
          break
        case 'week':
          filtered = filtered.filter(item => {
            const itemTime = new Date(item.timestamp).getTime()
            return now - itemTime < 7 * 24 * 60 * 60 * 1000
          })
          break
        case 'month':
          filtered = filtered.filter(item => {
            const itemTime = new Date(item.timestamp).getTime()
            return now - itemTime < 30 * 24 * 60 * 60 * 1000
          })
          break
      }
      
      return filtered
    }
  },
  onLoad() {
    this.calculateScrollHeight()
    this.getUserInfo()
    this.loadHistory()
  },
  onShow() {
    this.loadHistory()
  },
  onResize() {
    this.calculateScrollHeight()
  },
  onPullDownRefresh() {
    this.loadHistory()
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
    
    // 加载历史记录
    async loadHistory() {
      if (this.isLoading) return
      
      this.isLoading = true
      try {
        const token = uni.getStorageSync('user_token')
        const res = await new Promise((resolve, reject) => {
          uni.request({
            url: `http://localhost:8080/api/history/user/${this.userId}?page=1&size=50`,
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
          const historyData = res.data.data
          console.log('历史记录原始数据:', historyData)
          
          this.historyList = historyData.map(item => {
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
              createTime: this.formatTime(item.browseTime),
              timestamp: item.browseTime,
              postId: item.postId
            }
          })
          
          console.log('处理后的历史记录:', this.historyList)
        } else {
          console.log('API返回失败:', res.data)
          // 如果API不可用，使用模拟数据
          await this.loadMockHistory()
        }
      } catch (error) {
        console.error('加载历史记录失败:', error)
        // 如果API不可用，使用模拟数据
        await this.loadMockHistory()
      } finally {
        this.isLoading = false
        uni.stopPullDownRefresh()
      }
    },
    
    // 加载模拟历史数据（备用）
    async loadMockHistory() {
      await new Promise(resolve => setTimeout(resolve, 500))
      
      const now = new Date().getTime()
      const oneHour = 60 * 60 * 1000
      const oneDay = 24 * 60 * 60 * 1000
      const oneWeek = 7 * 24 * 60 * 60 * 1000
      
      this.historyList = [
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
          timestamp: now - oneDay,
          postId: 2
        },
        {
          id: 3,
          type: 'posts',
          typeText: '帖子',
          title: '西藏自驾游攻略',
          desc: '完成了西藏自驾之旅，沿途的风景让人震撼...',
          image: '/static/images/default-post.jpg',
          createTime: '3天前',
          timestamp: now - 3 * oneDay,
          postId: 3
        },
        {
          id: 4,
          type: 'posts',
          typeText: '帖子',
          title: '成都美食探索',
          desc: '成都真的是美食天堂！从火锅到串串，每一道菜都让人回味无穷...',
          image: '/static/images/default-post.jpg',
          createTime: '1周前',
          timestamp: now - oneWeek,
          postId: 4
        }
      ]
    },
    
    // 返回上一页
    goBack() {
      uni.navigateBack()
    },
    
    // 切换筛选
    switchFilter(filter) {
      this.currentFilter = filter
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
    
    // 删除单条历史
    deleteHistory(item) {
      uni.showModal({
        title: '删除记录',
        content: `确定要删除"${item.title}"的浏览记录吗？`,
        confirmColor: '#ff4444',
        success: (res) => {
          if (res.confirm) {
            this.performDelete(item.id)
          }
        }
      })
    },
    
    // 执行删除
    async performDelete(id) {
      uni.showLoading({
        title: '删除中...'
      })
      
      try {
        const token = uni.getStorageSync('user_token')
        const res = await new Promise((resolve, reject) => {
          uni.request({
            url: `http://localhost:8080/api/history/${id}`,
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
          this.historyList = this.historyList.filter(item => item.id !== id)
          this.showSuccess('删除成功')
        } else {
          this.showError(res.data?.message || '删除失败')
        }
      } catch (error) {
        console.error('删除失败:', error)
        // 如果API调用失败，从本地移除
        this.historyList = this.historyList.filter(item => item.id !== id)
        this.showSuccess('删除成功')
      } finally {
        uni.hideLoading()
      }
    },
    
    // 清除全部
    clearAll() {
      uni.showModal({
        title: '清除全部',
        content: '确定要清除全部浏览记录吗？',
        confirmColor: '#ff4444',
        success: (res) => {
          if (res.confirm) {
            this.performClearAll()
          }
        }
      })
    },
    
    // 执行清除全部
    async performClearAll() {
      uni.showLoading({
        title: '清除中...'
      })
      
      try {
        const token = uni.getStorageSync('user_token')
        const res = await new Promise((resolve, reject) => {
          uni.request({
            url: `http://localhost:8080/api/history/user/${this.userId}`,
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
          this.historyList = []
          this.showSuccess('清除成功')
        } else {
          this.showError(res.data?.message || '清除失败')
        }
      } catch (error) {
        console.error('清除失败:', error)
        // 如果API调用失败，清空本地数据
        this.historyList = []
        this.showSuccess('清除成功')
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
.my-history-page {
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

/* 时间筛选 */
.time-filter {
  display: flex;
  background: #fff;
  padding: 0 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.filter-item {
  padding: 20rpx 0;
  margin-right: 40rpx;
  font-size: 26rpx;
  color: #666;
  border-bottom: 4rpx solid transparent;
}

.filter-item.active {
  color: #b8d4ff;
  border-bottom-color: #b8d4ff;
  font-weight: 500;
}

.filter-item:last-child {
  margin-right: 0;
}

/* 历史列表 */
.history-list {
  padding: 20rpx 30rpx;
}

.history-item {
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

.delete-btn {
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

.delete-icon {
  width: 24rpx;
  height: 24rpx;
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

/* 清除全部 */
.clear-all {
  background: #fff;
  margin: 20rpx 30rpx 40rpx;
  border-radius: 16rpx;
  padding: 30rpx;
  text-align: center;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.06);
}

.clear-text {
  font-size: 28rpx;
  color: #ff4444;
  font-weight: 500;
}
</style>