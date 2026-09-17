<template>
  <view class="page-container">
    <!-- 页面头部 -->
    <view class="page-header">
      <view class="header-nav">
        <view class="nav-btn" @tap="goBack">
          <image src="/static/icons/general/back.png" class="nav-icon"></image>
        </view>
        <text class="header-title">行程详情</text>
        <view class="nav-btn" @tap="editTrip">
          <text class="edit-text">编辑</text>
        </view>
      </view>
    </view>

    <!-- 内容区域 -->
    <scroll-view class="content-scroll" scroll-y :style="{height: scrollHeight + 'px'}">
      <view class="detail-content" v-if="tripDetail">
        <!-- 基本信息 -->
        <view class="info-section">
          <text class="trip-name">{{ tripDetail.name }}</text>
          <view class="trip-status" :class="tripDetail.status">
            {{ getStatusText(tripDetail.status) }}
          </view>
        </view>

        <!-- 行程信息 -->
        <view class="detail-section">
          <view class="section-title">行程信息</view>
          <view class="info-grid">
            <view class="info-item">
              <image src="/static/icons/general/location.png" class="info-icon"></image>
              <view class="info-content">
                <text class="info-label">目的地</text>
                <text class="info-value">{{ tripDetail.destination }}</text>
              </view>
            </view>
            <view class="info-item">
              <image src="/static/icons/general/calendar.png" class="info-icon"></image>
              <view class="info-content">
                <text class="info-label">行程日期</text>
                <text class="info-value">{{ formatDateRange(tripDetail.startDate, tripDetail.endDate) }}</text>
              </view>
            </view>
            <view class="info-item">
              <image src="/static/icons/general/clock.png" class="info-icon"></image>
              <view class="info-content">
                <text class="info-label">行程天数</text>
                <text class="info-value">{{ calculateDays(tripDetail.startDate, tripDetail.endDate) }}天</text>
              </view>
            </view>
            <view class="info-item" v-if="tripDetail.budget">
              <image src="/static/icons/general/money.png" class="info-icon"></image>
              <view class="info-content">
                <text class="info-label">预算</text>
                <text class="info-value">¥{{ tripDetail.budget }}</text>
              </view>
            </view>
          </view>
        </view>

        <!-- 行程描述 -->
        <view class="detail-section" v-if="tripDetail.description">
          <view class="section-title">行程描述</view>
          <text class="description-text">{{ tripDetail.description }}</text>
        </view>

        <!-- 同行人员 -->
        <view class="detail-section" v-if="tripDetail.companions && tripDetail.companions.length > 0">
          <view class="section-title">同行人员</view>
          <view class="companions-list">
            <view class="companion-tag" v-for="(companion, index) in tripDetail.companions" :key="index">
              <text class="companion-name">{{ companion }}</text>
            </view>
          </view>
        </view>

        <!-- 注意事项 -->
        <view class="detail-section" v-if="tripDetail.notes">
          <view class="section-title">注意事项</view>
          <text class="notes-text">{{ tripDetail.notes }}</text>
        </view>

        <!-- 创建时间 -->
        <view class="detail-section">
          <view class="create-time">
            <text class="time-label">创建时间</text>
            <text class="time-value">{{ formatDate(tripDetail.createTime) }}</text>
          </view>
        </view>
      </view>

      <!-- 加载状态 -->
      <view class="loading-state" v-else>
        <image src="/static/icons/general/loading.png" class="loading-icon"></image>
        <text class="loading-text">加载中...</text>
      </view>

      <!-- 底部安全区域 -->
      <view class="safe-area"></view>
    </scroll-view>
  </view>
</template>

<script>
import { formatDate } from '@/utils/date.js'

export default {
  data() {
    return {
      tripDetail: null,
      scrollHeight: 0,
      tripId: null
    }
  },
  onLoad(options) {
    this.calculateScrollHeight()
    if (options.id) {
      this.tripId = options.id
      this.loadTripDetail(options.id)
    }
  },
  methods: {
    calculateScrollHeight() {
      const systemInfo = uni.getSystemInfoSync()
      const windowHeight = systemInfo.windowHeight
      const statusBarHeight = systemInfo.statusBarHeight || 0
      const navigationBarHeight = 44
      this.scrollHeight = windowHeight - statusBarHeight - navigationBarHeight
    },
    
    loadTripDetail(id) {
      try {
        const trips = uni.getStorageSync('user_trips') || []
        const trip = trips.find(t => t.id == id)
        if (trip) {
          this.tripDetail = trip
        } else {
          uni.showToast({
            title: '行程不存在',
            icon: 'none'
          })
          setTimeout(() => {
            uni.navigateBack()
          }, 1500)
        }
      } catch (error) {
        console.error('加载行程详情失败:', error)
        uni.showToast({
          title: '加载失败',
          icon: 'none'
        })
      }
    },
    
    goBack() {
      uni.navigateBack()
    },
    
    editTrip() {
      uni.navigateTo({
        url: `/pages/trip-edit/trip-edit?id=${this.tripId}`
      })
    },
    
    getStatusText(status) {
      const statusMap = {
        'planned': '计划中',
        'ongoing': '进行中',
        'completed': '已完成'
      }
      return statusMap[status] || '未知'
    },
    
    formatDateRange(startDate, endDate) {
      if (!startDate || !endDate) return ''
      return `${formatDate(startDate)} 至 ${formatDate(endDate)}`
    },
    
    calculateDays(startDate, endDate) {
      if (!startDate || !endDate) return 0
      const start = new Date(startDate)
      const end = new Date(endDate)
      const diffTime = Math.abs(end - start)
      return Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
    },
    
    formatDate
  }
}
</script>

<style scoped>
/* 详情页面样式 */
.page-container {
  min-height: 100vh;
  background-color: #f8f8f8;
}

.page-header {
  background: #fff;
  border-bottom: 1rpx solid #f0f0f0;
  padding: 0 30rpx;
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.header-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.nav-btn {
  padding: 16rpx;
}

.nav-icon {
  width: 32rpx;
  height: 32rpx;
}

.header-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.edit-text {
  font-size: 32rpx;
  color: #2c6be8;
  font-weight: 500;
}

.content-scroll {
  background: #f8f8f8;
}

.detail-content {
  background: #fff;
  margin-bottom: 20rpx;
  border-radius: 0;
}

.info-section {
  padding: 40rpx 30rpx;
  border-bottom: 1rpx solid #f8f8f8;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.trip-name {
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
  flex: 1;
}

.trip-status {
  font-size: 24rpx;
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
  background: #f0f0f0;
  color: #666;
}

.trip-status.planned {
  background: #e8f1ff;
  color: #2c6be8;
}

.trip-status.ongoing {
  background: #fff0e8;
  color: #ff6b35;
}

.trip-status.completed {
  background: #f0f8f0;
  color: #52c41a;
}

.detail-section {
  padding: 30rpx;
  border-bottom: 1rpx solid #f8f8f8;
}

.detail-section:last-child {
  border-bottom: none;
}

.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 20rpx;
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.info-item {
  display: flex;
  align-items: flex-start;
  gap: 20rpx;
}

.info-icon {
  width: 24rpx;
  height: 24rpx;
  margin-top: 4rpx;
  opacity: 0.7;
}

.info-content {
  flex: 1;
}

.info-label {
  font-size: 24rpx;
  color: #999;
  display: block;
  margin-bottom: 8rpx;
}

.info-value {
  font-size: 28rpx;
  color: #333;
  display: block;
}

.description-text,
.notes-text {
  font-size: 28rpx;
  color: #666;
  line-height: 1.6;
}

.companions-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.companion-tag {
  background: #e8f1ff;
  padding: 12rpx 20rpx;
  border-radius: 20rpx;
}

.companion-name {
  font-size: 24rpx;
  color: #2c6be8;
}

.create-time {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.time-label {
  font-size: 24rpx;
  color: #999;
}

.time-value {
  font-size: 24rpx;
  color: #666;
}

.loading-state {
  padding: 120rpx 0;
  text-align: center;
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
  color: #666;
}

.safe-area {
  height: env(safe-area-inset-bottom);
  background: #f8f8f8;
}
</style>