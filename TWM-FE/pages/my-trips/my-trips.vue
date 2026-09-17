<template>
  <view class="page-container">
    <!-- 页面头部 -->
    <view class="page-header">
      <view class="header-content">
        <text class="header-title">我的行程</text>
        <text class="header-subtitle">管理您的旅行计划</text>
      </view>
      <view class="header-bg"></view>
    </view>

    <!-- 内容区域 -->
    <scroll-view class="content-scroll" scroll-y :style="{height: scrollHeight + 'px'}" @refresherrefresh="onRefresh" refresher-enabled>
      <!-- 新建行程按钮 -->
      <view class="create-section">
        <view class="create-card">
          <view class="create-header">
            <image src="/static/icons/general/add.png" class="create-icon"></image>
            <text class="create-title">创建新行程</text>
          </view>
          <text class="create-desc">开始规划您的下一次旅行冒险</text>
          <view class="create-btn" @tap="createTrip">
            <text class="create-btn-text">新建行程</text>
            <image src="/static/icons/general/arrow-right.png" class="create-arrow"></image>
          </view>
        </view>
      </view>

      <!-- 行程列表 -->
      <view class="list-section" v-if="trips.length > 0">
        <view class="section-header">
          <view class="section-title-wrapper">
            <image src="/static/icons/general/trip.png" class="section-icon"></image>
            <text class="section-title">我的行程计划</text>
          </view>
          <text class="section-count">{{ trips.length }}个行程</text>
        </view>
        
        <view class="trip-list">
          <view 
            class="trip-card" 
            v-for="trip in trips" 
            :key="trip.id"
            @tap="viewTripDetail(trip.id)"
          >
            <view class="card-header">
              <view class="trip-basic">
                <text class="trip-name">{{ trip.name }}</text>
                <view class="trip-status" :class="trip.status">
                  {{ getStatusText(trip.status) }}
                </view>
              </view>
              <view class="trip-date-badge">
                <text class="date-text">{{ calculateDays(trip.startDate, trip.endDate) }}天</text>
              </view>
            </view>
            
            <view class="trip-info">
              <view class="info-row">
                <view class="info-item">
                  <image src="/static/icons/general/location.png" class="info-icon"></image>
                  <text class="info-text">{{ trip.destination }}</text>
                </view>
              </view>
              <view class="info-row">
                <view class="info-item">
                  <image src="/static/icons/general/calendar.png" class="info-icon"></image>
                  <text class="info-text">{{ formatDateRange(trip.startDate, trip.endDate) }}</text>
                </view>
              </view>
            </view>
            
            <view class="trip-desc">
              <text class="desc-text">{{ trip.description }}</text>
            </view>
            
            <view class="card-footer">
              <view class="trip-meta">
                <text class="meta-text">{{ formatDate(trip.createTime) }} 创建</text>
              </view>
              <view class="trip-actions">
                <view class="action-btn edit" @tap.stop="editTrip(trip.id)">
                  <image src="/static/icons/general/edit.png" class="action-icon"></image>
                  <text class="action-text">编辑</text>
                </view>
                <view class="action-btn delete" @tap.stop="deleteTrip(trip.id)">
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
          <image src="/static/icons/general/trip.png" class="empty-icon"></image>
          <text class="empty-title">暂无行程计划</text>
          <text class="empty-desc">开始规划您的第一次旅行吧</text>
          <view class="empty-btn" @tap="createTrip">
            <text class="empty-btn-text">创建第一个行程</text>
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
      trips: [],
      loading: false,
      scrollHeight: 0
    }
  },
  onLoad() {
    this.calculateScrollHeight()
    this.loadTrips()
  },
  onShow() {
    this.loadTrips()
  },
  onPullDownRefresh() {
    this.loadTrips()
  },
  methods: {
    calculateScrollHeight() {
      const systemInfo = uni.getSystemInfoSync()
      const windowHeight = systemInfo.windowHeight
      const statusBarHeight = systemInfo.statusBarHeight || 0
      const navigationBarHeight = 44
      this.scrollHeight = windowHeight - statusBarHeight - navigationBarHeight - 120
    },
    
    async loadTrips() {
      this.loading = true
      try {
        await new Promise(resolve => setTimeout(resolve, 800))
        
        let savedTrips = uni.getStorageSync('user_trips') || []
        
        // 如果没有数据，添加一些示例数据
        if (savedTrips.length === 0) {
          savedTrips = [
            {
              id: 1,
              name: '云南大理之旅',
              destination: '大理, 云南',
              startDate: '2024-03-15',
              endDate: '2024-03-20',
              status: 'completed',
              description: '探索苍山洱海，感受白族文化',
              budget: '5000',
              companions: ['张三', '李四'],
              notes: '记得带防晒霜和相机',
              createTime: '2024-01-10T08:00:00'
            },
            {
              id: 2,
              name: '成都美食探索',
              destination: '成都, 四川',
              startDate: '2024-04-10',
              endDate: '2024-04-13',
              status: 'planned',
              description: '品尝地道川菜，参观熊猫基地',
              budget: '3000',
              companions: ['王五'],
              notes: '提前预订火锅餐厅',
              createTime: '2024-02-15T10:30:00'
            },
            {
              id: 3,
              name: '厦门海边度假',
              destination: '厦门, 福建',
              startDate: '2024-05-01',
              endDate: '2024-05-05',
              status: 'ongoing',
              description: '鼓浪屿漫步，环岛路骑行',
              budget: '4000',
              companions: ['赵六', '钱七'],
              notes: '准备泳衣和沙滩装备',
              createTime: '2024-03-01T14:20:00'
            }
          ]
          uni.setStorageSync('user_trips', savedTrips)
        }
        
        this.trips = savedTrips.map(trip => ({
          ...trip,
          startDate: trip.startDate || formatDate(new Date()),
          endDate: trip.endDate || formatDate(new Date())
        }))
      } catch (error) {
        console.error('加载行程失败:', error)
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
      this.loadTrips()
    },
    
    createTrip() {
      uni.navigateTo({
        url: '/pages/trip-edit/trip-edit'
      })
    },
    
    editTrip(id) {
      uni.navigateTo({
        url: `/pages/trip-edit/trip-edit?id=${id}`
      })
    },
    
    viewTripDetail(id) {
      uni.navigateTo({
        url: `/pages/trip-detail/trip-detail?id=${id}`
      })
    },
    
    deleteTrip(id) {
      uni.showModal({
        title: '删除行程',
        content: '确定要删除这个行程吗？此操作不可恢复。',
        confirmColor: '#ff6b6b',
        success: (res) => {
          if (res.confirm) {
            this.performDeleteTrip(id)
          }
        }
      })
    },
    
    async performDeleteTrip(id) {
      try {
        this.trips = this.trips.filter(trip => trip.id !== id)
        uni.setStorageSync('user_trips', this.trips)
        uni.showToast({
          title: '删除成功',
          icon: 'success'
        })
      } catch (error) {
        console.error('删除行程失败:', error)
        uni.showToast({
          title: '删除失败',
          icon: 'none'
        })
      }
    },
    
    getStatusText(status) {
      const statusMap = {
        'planned': '计划中',
        'ongoing': '进行中',
        'completed': '已完成',
        'cancelled': '已取消'
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
    
    formatDate(dateStr) {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      const month = date.getMonth() + 1
      const day = date.getDate()
      return `${month}月${day}日`
    }
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

/* 新建行程卡片 - 清新蓝色风格 */
.create-section {
  padding: 30rpx;
}

.create-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fbff 100%);
  border-radius: 24rpx;
  padding: 40rpx;
  box-shadow: 0 8rpx 32rpx rgba(184, 212, 255, 0.3);
  border: 1rpx solid #d1e3ff;
}

.create-header {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
}

.create-icon {
  width: 24rpx;
  height: 24rpx;
  margin-right: 16rpx;
}

.create-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #2c5282;
}

.create-desc {
  font-size: 26rpx;
  color: #5a7ca8;
  margin-bottom: 32rpx;
  line-height: 1.5;
}

.create-btn {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #b8d4ff 0%, #bcc4e8 100%);
  border-radius: 16rpx;
  padding: 24rpx 32rpx;
  box-shadow: 0 4rpx 16rpx rgba(139, 185, 255, 0.4);
}

.create-btn-text {
  font-size: 28rpx;
  color: #2c5282;
  font-weight: 600;
}

.create-arrow {
  width: 24rpx;
  height: 24rpx;
}

/* 行程列表 - 清新蓝色风格 */
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

.trip-list {
  padding: 0 30rpx;
}

.trip-card {
  background: #ffffff;
  border-radius: 20rpx;
  padding: 32rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 4rpx 24rpx rgba(184, 212, 255, 0.3);
  border: 1rpx solid #e1edff;
  transition: all 0.3s ease;
}

.trip-card:active {
  transform: translateY(2rpx);
  box-shadow: 0 2rpx 12rpx rgba(184, 212, 255, 0.4);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24rpx;
}

.trip-basic {
  flex: 1;
}

.trip-name {
  font-size: 34rpx;
  font-weight: 700;
  color: #2c5282;
  display: block;
  margin-bottom: 12rpx;
  line-height: 1.3;
}

.trip-status {
  display: inline-block;
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  border-radius: 20rpx;
  font-weight: 500;
}

.trip-status.planned {
  background: rgba(184, 212, 255, 0.3);
  color: #2c5282;
  border: 1rpx solid #b8d4ff;
}

.trip-status.ongoing {
  background: rgba(255, 193, 7, 0.2);
  color: #e6a700;
  border: 1rpx solid #ffc107;
}

.trip-status.completed {
  background: rgba(76, 175, 80, 0.2);
  color: #4caf50;
  border: 1rpx solid #4caf50;
}

.trip-date-badge {
  background: linear-gradient(135deg, #b8d4ff 0%, #8bb9ff 100%);
  padding: 8rpx 16rpx;
  border-radius: 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(139, 185, 255, 0.3);
}

.date-text {
  font-size: 22rpx;
  color: #2c5282;
  font-weight: 600;
}

.trip-info {
  margin-bottom: 20rpx;
}

.info-row {
  margin-bottom: 12rpx;
}

.info-item {
  display: flex;
  align-items: center;
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

.trip-desc {
  margin-bottom: 24rpx;
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

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20rpx;
  border-top: 1rpx solid #e1edff;
}

.trip-meta {
  flex: 1;
}

.meta-text {
  font-size: 24rpx;
  color: #a0bcd8;
}

.trip-actions {
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

.action-btn.edit {
  background: rgba(184, 212, 255, 0.3);
  border: 1rpx solid #b8d4ff;
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

.action-btn.edit .action-icon {
  opacity: 0.8;
}

.action-btn.delete .action-icon {
  opacity: 0.8;
}

.action-text {
  font-size: 24rpx;
  font-weight: 500;
}

.action-btn.edit .action-text {
  color: #2c5282;
}

.action-btn.delete .action-text {
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