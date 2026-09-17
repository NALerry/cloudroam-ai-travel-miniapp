<template>
  <view class="page-container">
    <!-- 页面头部 -->
    <view class="page-header">
      <view class="header-content">
        <text class="header-title">地点收藏</text>
        <text class="header-subtitle">您收藏的旅行地点</text>
      </view>
      <view class="header-bg"></view>
    </view>

    <!-- 内容区域 -->
    <scroll-view class="content-scroll" scroll-y :style="{height: scrollHeight + 'px'}" @refresherrefresh="onRefresh" refresher-enabled>
      <!-- 筛选标签 -->
      <view class="filter-section">
        <scroll-view class="filter-scroll" scroll-x>
          <view class="filter-tags">
            <view 
              class="filter-tag" 
              :class="{ active: currentFilter === 'all' }"
              @tap="changeFilter('all')"
            >
              全部
            </view>
            <view 
              class="filter-tag" 
              :class="{ active: currentFilter === 'scenic' }"
              @tap="changeFilter('scenic')"
            >
              景点
            </view>
            <view 
              class="filter-tag" 
              :class="{ active: currentFilter === 'food' }"
              @tap="changeFilter('food')"
            >
              美食
            </view>
            <view 
              class="filter-tag" 
              :class="{ active: currentFilter === 'hotel' }"
              @tap="changeFilter('hotel')"
            >
              住宿
            </view>
            <view 
              class="filter-tag" 
              :class="{ active: currentFilter === 'shopping' }"
              @tap="changeFilter('shopping')"
            >
              购物
            </view>
          </view>
        </scroll-view>
      </view>

      <!-- 收藏列表 -->
      <view class="list-section" v-if="filteredBookmarks.length > 0">
        <view class="section-header">
          <view class="section-title-wrapper">
            <image src="/static/icons/general/gps.png" class="section-icon"></image>
            <text class="section-title">收藏的地点</text>
          </view>
          <text class="section-count">{{ filteredBookmarks.length }}个地点</text>
        </view>
        
        <view class="bookmark-list">
          <view 
            class="bookmark-card" 
            v-for="bookmark in filteredBookmarks" 
            :key="bookmark.id"
            @tap="viewPlaceDetail(bookmark.id)"
          >
            <view class="card-header">
              <view class="bookmark-basic">
                <text class="bookmark-name">{{ bookmark.name }}</text>
                <view class="bookmark-rating">
                  <image src="/static/icons/general/star.png" class="star-icon"></image>
                  <text class="rating-text">{{ bookmark.rating }}</text>
                </view>
              </view>
              <view class="bookmark-type" :class="bookmark.type">
                {{ getTypeText(bookmark.type) }}
              </view>
            </view>
            
            <view class="bookmark-info">
              <view class="info-row">
                <view class="info-item">
                  <image src="/static/icons/general/location.png" class="info-icon"></image>
                  <text class="info-text">{{ bookmark.address }}</text>
                </view>
              </view>
              <view class="info-row">
                <view class="info-item">
                  <image src="/static/icons/general/distance.png" class="info-icon"></image>
                  <text class="info-text">{{ bookmark.distance }}</text>
                </view>
                <view class="info-item">
                  <image src="/static/icons/general/tag.png" class="info-icon"></image>
                  <text class="info-text">{{ bookmark.price }}</text>
                </view>
              </view>
            </view>
            
            <view class="bookmark-desc">
              <text class="desc-text">{{ bookmark.description || '暂无描述' }}</text>
            </view>
            
            <view class="bookmark-tags">
              <view class="tag" v-for="tag in bookmark.tags.slice(0, 3)" :key="tag">
                {{ tag }}
              </view>
            </view>
            
            <view class="card-footer">
              <view class="bookmark-meta">
                <text class="meta-text">收藏于 {{ formatDate(bookmark.createTime) }}</text>
              </view>
              <view class="bookmark-actions">
                <view class="action-btn delete" @tap.stop="removeBookmark(bookmark.id)">
                  <image src="/static/icons/general/delete.png" class="action-icon"></image>
                  <text class="action-text">删除</text>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <view class="empty-state" v-else>
        <view class="empty-content">
          <image src="/static/icons/general/gps.png" class="empty-icon"></image>
          <text class="empty-title">暂无收藏地点</text>
          <text class="empty-desc">在探索中发现并收藏您喜欢的地点</text>
          <view class="empty-btn" @tap="goExplore">
            <text class="empty-btn-text">去探索</text>
          </view>
        </view>
      </view>

      <!-- 底部安全区域 -->
      <view class="safe-area"></view>
    </scroll-view>

    <!-- 加载状态 -->
    <view class="loading-mask" v-if="loading">
      <view class="loading-content">
        <image src="/static/icons/general/loading.png" class="loading-icon"></image>
        <text class="loading-text">加载中...</text>
      </view>
    </view>
  </view>
</template>

<script>
import { formatDate } from '@/utils/date.js'

export default {
  data() {
    return {
      bookmarks: [],
      currentFilter: 'all',
      loading: false,
      scrollHeight: 0
    }
  },
  computed: {
    filteredBookmarks() {
      if (this.currentFilter === 'all') {
        return this.bookmarks
      }
      return this.bookmarks.filter(item => item.type === this.currentFilter)
    }
  },
  onLoad() {
    this.calculateScrollHeight()
    this.loadBookmarks()
  },
  onShow() {
    this.loadBookmarks()
  },
  onPullDownRefresh() {
    this.loadBookmarks()
  },
  methods: {
    calculateScrollHeight() {
      const systemInfo = uni.getSystemInfoSync()
      const windowHeight = systemInfo.windowHeight
      const statusBarHeight = systemInfo.statusBarHeight || 0
      const navigationBarHeight = 44
      this.scrollHeight = windowHeight - statusBarHeight - navigationBarHeight - 120
    },
    
    async loadBookmarks() {
      this.loading = true
      try {
        await new Promise(resolve => setTimeout(resolve, 800))
        
        const savedBookmarks = uni.getStorageSync('user_bookmarks') || []
        this.bookmarks = savedBookmarks.map(bookmark => ({
          ...bookmark,
          createTime: bookmark.createTime || new Date().toISOString(),
          tags: bookmark.tags || []
        }))
      } catch (error) {
        console.error('加载收藏失败:', error)
        uni.showToast({
          title: '加载失败',
          icon: 'none'
        })
      } finally {
        this.loading = false
        uni.stopPullDownRefresh()
      }
    },
    
    onRefresh() {
      this.loadBookmarks()
    },
    
    changeFilter(type) {
      this.currentFilter = type
    },
    
    getTypeText(type) {
      const typeMap = {
        'scenic': '景点',
        'food': '美食',
        'hotel': '住宿',
        'shopping': '购物'
      }
      return typeMap[type] || '地点'
    },
    
    viewPlaceDetail(id) {
      uni.navigateTo({
        url: `/pages/place-detail/place-detail?id=${id}`
      })
    },
    
    removeBookmark(id) {
      uni.showModal({
        title: '取消收藏',
        content: '确定要取消收藏这个地点吗？',
        confirmColor: '#ff6b6b',
        success: (res) => {
          if (res.confirm) {
            this.performRemoveBookmark(id)
          }
        }
      })
    },
    
    async performRemoveBookmark(id) {
      try {
        this.bookmarks = this.bookmarks.filter(item => item.id !== id)
        uni.setStorageSync('user_bookmarks', this.bookmarks)
        uni.showToast({
          title: '已取消收藏',
          icon: 'success'
        })
      } catch (error) {
        console.error('取消收藏失败:', error)
        uni.showToast({
          title: '操作失败',
          icon: 'none'
        })
      }
    },
    
    goExplore() {
      uni.switchTab({
        url: '/pages/map/map'
      })
    },
    
    formatDate
  }
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #b8d4ff 0%, #8bb9ff 100%);
}

/* 页面头部 - 清新蓝色背景 */
.page-header {
  position: relative;
  height: 280rpx;
  overflow: hidden;
}

.header-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #b8d4ff 0%, #8bb9ff 100%);
}

.header-content {
  position: relative;
  z-index: 2;
  padding: 80rpx 30rpx 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.header-title {
  font-size: 42rpx;
  font-weight: 700;
  color: #2c5282;
  margin-bottom: 16rpx;
  text-shadow: 0 2rpx 8rpx rgba(255, 255, 255, 0.5);
}

.header-subtitle {
  font-size: 28rpx;
  color: #4a7bb8;
  font-weight: 400;
}

/* 内容区域 */
.content-scroll {
  margin-top: -40rpx;
  border-top-left-radius: 40rpx;
  border-top-right-radius: 40rpx;
  background: #f0f7ff;
  position: relative;
  z-index: 3;
}

/* 筛选标签 - 清新蓝色风格 */
.filter-section {
  padding: 30rpx;
  background: transparent;
}

.filter-scroll {
  white-space: nowrap;
}

.filter-tags {
  display: inline-flex;
  gap: 16rpx;
}

.filter-tag {
  padding: 16rpx 32rpx;
  border-radius: 30rpx;
  font-size: 26rpx;
  background: rgba(255, 255, 255, 0.3);
  border: 1rpx solid rgba(255, 255, 255, 0.5);
  color: #2c5282;
  flex-shrink: 0;
}

.filter-tag.active {
  background: #ffffff;
  box-shadow: 0 4rpx 16rpx rgba(139, 185, 255, 0.3);
  border: 1rpx solid #b8d4ff;
  color: #2c6be8;
  font-weight: 600;
}

/* 列表样式 */
.list-section {
  background: transparent;
  margin-bottom: 20rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 30rpx 24rpx;
}

.section-title-wrapper {
  display: flex;
  align-items: center;
}

.section-icon {
  width: 28rpx;
  height: 28rpx;
  margin-right: 12rpx;
  opacity: 0.8;
}

.section-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #2c5282;
}

.section-count {
  font-size: 26rpx;
  color: #5a7ca8;
  background: rgba(184, 212, 255, 0.5);
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
  font-weight: 500;
}

.bookmark-list {
  padding: 0 30rpx;
}

.bookmark-card {
  background: #ffffff;
  border-radius: 20rpx;
  padding: 32rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 4rpx 24rpx rgba(184, 212, 255, 0.3);
  border: 1rpx solid #e1edff;
  transition: all 0.3s ease;
}

.bookmark-card:active {
  transform: translateY(2rpx);
  box-shadow: 0 2rpx 12rpx rgba(184, 212, 255, 0.4);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24rpx;
}

.bookmark-basic {
  flex: 1;
}

.bookmark-name {
  font-size: 34rpx;
  font-weight: 700;
  color: #2c5282;
  display: block;
  margin-bottom: 12rpx;
  line-height: 1.3;
}

.bookmark-rating {
  display: flex;
  align-items: center;
}

.star-icon {
  width: 24rpx;
  height: 24rpx;
  margin-right: 4rpx;
}

.rating-text {
  font-size: 24rpx;
  color: #ff6b35;
  font-weight: 500;
}

.bookmark-type {
  display: inline-block;
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  border-radius: 20rpx;
  font-weight: 500;
}

.bookmark-type.scenic {
  background: rgba(184, 212, 255, 0.3);
  color: #2c5282;
  border: 1rpx solid #b8d4ff;
}

.bookmark-type.food {
  background: rgba(255, 193, 7, 0.2);
  color: #e6a700;
  border: 1rpx solid #ffc107;
}

.bookmark-type.hotel {
  background: rgba(76, 175, 80, 0.2);
  color: #4caf50;
  border: 1rpx solid #4caf50;
}

.bookmark-type.shopping {
  background: rgba(139, 185, 255, 0.3);
  color: #2c6be8;
  border: 1rpx solid #8bb9ff;
}

.bookmark-info {
  margin-bottom: 20rpx;
}

.info-row {
  display: flex;
  margin-bottom: 12rpx;
}

.info-item {
  display: flex;
  align-items: center;
  margin-right: 30rpx;
}

.info-icon {
  width: 20rpx;
  height: 20rpx;
  margin-right: 12rpx;
  opacity: 0.6;
}

.info-text {
  font-size: 26rpx;
  color: #5a7ca8;
}

.bookmark-desc {
  margin-bottom: 20rpx;
  padding: 20rpx;
  background: #f8fbff;
  border-radius: 12rpx;
  border-left: 4rpx solid #b8d4ff;
}

.desc-text {
  font-size: 26rpx;
  color: #5a7ca8;
  line-height: 1.5;
}

.bookmark-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-bottom: 20rpx;
}

.tag {
  background: rgba(184, 212, 255, 0.3);
  padding: 6rpx 16rpx;
  border-radius: 16rpx;
  border: 1rpx solid rgba(184, 212, 255, 0.5);
  font-size: 22rpx;
  color: #2c5282;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20rpx;
  border-top: 1rpx solid #e1edff;
}

.bookmark-meta {
  flex: 1;
}

.meta-text {
  font-size: 24rpx;
  color: #a0bcd8;
}

.bookmark-actions {
  display: flex;
  gap: 16rpx;
}

.action-btn {
  display: flex;
  align-items: center;
  padding: 12rpx 20rpx;
  border-radius: 12rpx;
  transition: all 0.3s ease;
}

.action-btn.delete {
  background: rgba(255, 107, 107, 0.1);
  border: 1rpx solid #ff6b6b;
}

.action-btn:active {
  transform: scale(0.95);
}

.action-icon {
  width: 20rpx;
  height: 20rpx;
  margin-right: 8rpx;
}

.action-text {
  font-size: 24rpx;
  font-weight: 500;
  color: #ff6b6b;
}

/* 空状态 */
.empty-state {
  background: transparent;
  padding: 120rpx 60rpx;
}

.empty-content {
  text-align: center;
  background: #ffffff;
  padding: 80rpx 40rpx;
  border-radius: 24rpx;
  box-shadow: 0 4rpx 24rpx rgba(184, 212, 255, 0.3);
  border: 1rpx solid #e1edff;
}

.empty-icon {
  width: 120rpx;
  height: 120rpx;
  margin-bottom: 32rpx;
  opacity: 0.5;
}

.empty-title {
  font-size: 32rpx;
  color: #2c5282;
  display: block;
  margin-bottom: 16rpx;
  font-weight: 600;
}

.empty-desc {
  font-size: 26rpx;
  color: #5a7ca8;
  display: block;
  margin-bottom: 40rpx;
  line-height: 1.5;
}

.empty-btn {
  background: linear-gradient(135deg, #b8d4ff 0%, #8bb9ff 100%);
  border-radius: 16rpx;
  padding: 24rpx 48rpx;
  display: inline-block;
  box-shadow: 0 4rpx 16rpx rgba(139, 185, 255, 0.4);
}

.empty-btn-text {
  font-size: 28rpx;
  color: #2c5282;
  font-weight: 600;
}

/* 加载状态 */
.loading-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(184, 212, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-content {
  background: #ffffff;
  padding: 40rpx;
  border-radius: 20rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 8rpx 32rpx rgba(184, 212, 255, 0.4);
  border: 1rpx solid #e1edff;
}

.loading-icon {
  width: 60rpx;
  height: 60rpx;
  margin-bottom: 20rpx;
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 28rpx;
  color: #5a7ca8;
  font-weight: 500;
}

/* 安全区域 */
.safe-area {
  height: env(safe-area-inset-bottom);
  background: #f0f7ff;
}
</style>