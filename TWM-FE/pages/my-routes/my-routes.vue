<template>
  <view class="page-container">
    <!-- 页面头部 -->
    <view class="page-header">
      <view class="header-content">
        <text class="header-title">我的路线</text>
        <text class="header-subtitle">管理您的旅行路线</text>
      </view>
      <view class="header-bg"></view>
    </view>

    <!-- 内容区域 -->
    <scroll-view class="content-scroll" scroll-y :style="{height: scrollHeight + 'px'}" @refresherrefresh="onRefresh" refresher-enabled>
      <!-- 新建路线按钮 -->
      <view class="create-section">
        <view class="create-card">
          <view class="create-header">
            <image src="/static/icons/general/add.png" class="create-icon" mode="aspectFit"></image>
            <text class="create-title">创建新路线</text>
          </view>
          <text class="create-desc">规划您的专属旅行路线</text>
          <view class="create-btn" @tap="createRoute">
            <text class="create-btn-text">新建路线</text>
            <image src="/static/icons/general/arrow-right.png" class="create-arrow" mode="aspectFit"></image>
          </view>
        </view>
      </view>

      <!-- 路线列表 -->
      <view class="list-section" v-if="routes.length > 0">
        <view class="section-header">
          <view class="section-title-wrapper">
            <image src="/static/icons/general/path.png" class="section-icon" mode="aspectFit"></image>
            <text class="section-title">我的旅行路线</text>
          </view>
          <text class="section-count">{{ routes.length }}条路线</text>
        </view>
        
        <view class="route-list">
          <view 
            class="route-card" 
            v-for="route in routes" 
            :key="route.id"
            @tap="viewRouteDetail(route.id)"
          >
            <view class="card-header">
              <view class="route-basic">
                <text class="route-name">{{ route.name }}</text>
              </view>
              <view class="route-duration-badge">
                <text class="duration-text">{{ route.duration }}天</text>
              </view>
            </view>
            
            <view class="route-info">
              <view class="info-row">
                <view class="info-item">
                  <image src="/static/icons/general/gps.png" class="info-icon" mode="aspectFit"></image>
                  <text class="info-text">{{ route.places.join(' → ') }}</text>
                </view>
              </view>
              <view class="info-row">
                <view class="info-item">
                  <image src="/static/icons/general/distance.png" class="info-icon" mode="aspectFit"></image>
                  <text class="info-text">{{ route.distance }}km</text>
                </view>
                <view class="info-item">
                  <image src="/static/icons/general/flag.png" class="info-icon" mode="aspectFit"></image>
                  <text class="info-text">{{ route.places.length }}个地点</text>
                </view>
              </view>
            </view>
            
            <view class="route-desc">
              <text class="desc-text">{{ route.description }}</text>
            </view>
            
            <view class="route-tags">
              <view class="tag" v-for="tag in route.tags" :key="tag">
                {{ tag }}
              </view>
            </view>
            
            <view class="card-footer">
              <view class="route-meta">
                <text class="meta-text">{{ formatDate(route.createTime) }} 创建</text>
              </view>
              <view class="route-actions">
                <view class="action-btn view-map" @tap.stop="goToMapWithRoute(route)">
                  <image src="/static/icons/general/map.png" class="action-icon" mode="aspectFit"></image>
                  <text class="action-text">查看地图</text>
                </view>
                <view class="action-btn edit" @tap.stop="editRoute(route.id)">
                  <image src="/static/icons/general/edit.png" class="action-icon" mode="aspectFit"></image>
                  <text class="action-text">编辑</text>
                </view>
                <view class="action-btn delete" @tap.stop="deleteRoute(route.id)">
                  <image src="/static/icons/general/delete.png" class="action-icon" mode="aspectFit"></image>
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
          <image src="/static/icons/general/path1.png" class="empty-icon" mode="aspectFit"></image>
          <text class="empty-title">暂无旅行路线</text>
          <text class="empty-desc">创建您的第一条旅行路线</text>
          <view class="empty-btn" @tap="createRoute">
            <text class="empty-btn-text">创建第一个路线</text>
          </view>
        </view>
      </view>

      <!-- 底部安全区域 -->
      <view class="safe-area"></view>
    </scroll-view>

    <!-- 加载状态 -->
    <view class="loading-mask" v-if="loading">
      <view class="loading-content">
        <image src="/static/icons/general/loading.png" class="loading-icon" mode="aspectFit"></image>
        <text class="loading-text">加载中...</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      routes: [],
      loading: false,
      scrollHeight: 0
    }
  },
  onLoad() {
    this.calculateScrollHeight()
    this.loadRoutes()
    this.setupEventListeners()
  },
  onShow() {
    this.loadRoutes()
  },
  onUnload() {
    this.removeEventListeners()
  },
  onPullDownRefresh() {
    this.loadRoutes()
  },
  methods: {
    setupEventListeners() {
      uni.$on('routesUpdated', this.handleRoutesUpdated)
    },
    
    removeEventListeners() {
      uni.$off('routesUpdated', this.handleRoutesUpdated)
    },
    
    handleRoutesUpdated() {
      console.log('my-routes.vue: 收到行程规划更新事件，重新加载数据')
      this.loadRoutes()
    },
    
    calculateScrollHeight() {
      const systemInfo = uni.getSystemInfoSync()
      const windowHeight = systemInfo.windowHeight
      const statusBarHeight = systemInfo.statusBarHeight || 0
      const navigationBarHeight = 44
      this.scrollHeight = windowHeight - statusBarHeight - navigationBarHeight - 120
    },
    
    async loadRoutes() {
      this.loading = true
      try {
        await new Promise(resolve => setTimeout(resolve, 500))
        
        let savedRoutes = uni.getStorageSync('user_routes') || []
        
        if (savedRoutes.length === 0) {
          savedRoutes = [
            {
              id: 1,
              name: '云南经典环线',
              description: '大理-丽江-香格里拉经典路线，感受云南的自然风光和少数民族文化',
              places: ['大理', '丽江', '香格里拉'],
              duration: 7,
              distance: 800,
              tags: ['经典', '自然', '文化'],
              createTime: '2024-01-15T10:00:00'
            },
            {
              id: 2,
              name: '成都美食之旅',
              description: '探索成都地道美食文化，体验悠闲的巴蜀生活',
              places: ['宽窄巷子', '锦里', '春熙路'],
              duration: 3,
              distance: 50,
              tags: ['美食', '城市', '文化'],
              createTime: '2024-02-20T14:30:00'
            },
            {
              id: 3,
              name: '厦门环岛路线',
              description: '环岛路骑行，感受海滨风情，品尝特色海鲜',
              places: ['鼓浪屿', '环岛路', '曾厝垵'],
              duration: 4,
              distance: 120,
              tags: ['海滨', '骑行', '休闲'],
              createTime: '2024-03-10T09:15:00'
            }
          ]
          uni.setStorageSync('user_routes', savedRoutes)
        }
        
        this.routes = savedRoutes.map(route => ({
          ...route,
          createTime: route.createTime || new Date().toISOString(),
          places: route.places || [],
          tags: route.tags || []
        }))
        
        console.log('my-routes.vue: 加载行程规划数据:', this.routes.length, '条')
      } catch (error) {
        console.error('加载路线失败:', error)
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
      this.loadRoutes()
    },
    
    createRoute() {
      console.log('创建新路线')
      uni.navigateTo({
        url: '/pages/route-edit/route-edit',
        success: (res) => {
          console.log('跳转到路线编辑页面成功')
        },
        fail: (err) => {
          console.error('跳转到路线编辑页面失败:', err)
          uni.showToast({
            title: '页面跳转失败',
            icon: 'none'
          })
        }
      })
    },
    
    editRoute(id) {
      console.log('编辑路线:', id)
      uni.navigateTo({
        url: `/pages/route-edit/route-edit?id=${id}`,
        success: (res) => {
          console.log('跳转到路线编辑页面成功')
        },
        fail: (err) => {
          console.error('跳转到路线编辑页面失败:', err)
          uni.showToast({
            title: '页面跳转失败',
            icon: 'none'
          })
        }
      })
    },
    
    // 修复：跳转到地图页面（tabBar页面）
    goToMapWithRoute(route) {
      console.log('跳转到地图页面，路线:', route)
      
      // 使用 switchTab 跳转到 tabBar 页面
      uni.switchTab({
        url: '/pages/map/map',
        success: (res) => {
          console.log('成功跳转到地图页面')
          
          // 由于 switchTab 不能传递参数，我们需要使用全局事件来传递 routeId
          // 延迟一下确保地图页面已经加载
          setTimeout(() => {
            uni.$emit('loadRouteOnMap', route.id)
            console.log('发送加载路线事件，routeId:', route.id)
          }, 500)
        },
        fail: (err) => {
          console.error('跳转失败:', err)
          uni.showToast({
            title: '跳转失败',
            icon: 'none'
          })
        }
      })
    },
    
    viewRouteDetail(id) {
      console.log('查看路线详情:', id)
      uni.navigateTo({
        url: `/pages/route-detail/route-detail?id=${id}`,
        success: (res) => {
          console.log('跳转到路线详情页面成功')
        },
        fail: (err) => {
          console.error('跳转到路线详情页面失败:', err)
          uni.showToast({
            title: '页面跳转失败',
            icon: 'none'
          })
        }
      })
    },
    
    deleteRoute(id) {
      uni.showModal({
        title: '删除路线',
        content: '确定要删除这条路线吗？此操作不可恢复。',
        confirmColor: '#ff6b6b',
        success: (res) => {
          if (res.confirm) {
            this.performDeleteRoute(id)
          }
        }
      })
    },
    
    async performDeleteRoute(id) {
      try {
        let savedRoutes = uni.getStorageSync('user_routes') || []
        savedRoutes = savedRoutes.filter(route => route.id !== id)
        uni.setStorageSync('user_routes', savedRoutes)
        
        this.routes = this.routes.filter(route => route.id !== id)
        
        uni.$emit('routesUpdated')
        
        uni.showToast({
          title: '删除成功',
          icon: 'success'
        })
      } catch (error) {
        console.error('删除路线失败:', error)
        uni.showToast({
          title: '删除失败',
          icon: 'none'
        })
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    }
  }
}
</script>

<style scoped>
/* 样式保持不变，与之前相同 */
.page-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #b8d4ff 0%, #8bb9ff 100%);
}

.page-header {
  position: relative;
  height: 220rpx;
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
  padding: 60rpx 30rpx 30rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.header-title {
  font-size: 38rpx;
  font-weight: 700;
  color: #2c5282;
  margin-bottom: 12rpx;
  text-shadow: 0 2rpx 8rpx rgba(255, 255, 255, 0.5);
}

.header-subtitle {
  font-size: 26rpx;
  color: #4a7bb8;
  font-weight: 400;
}

.content-scroll {
  margin-top: -30rpx;
  border-top-left-radius: 40rpx;
  border-top-right-radius: 40rpx;
  background: #f0f7ff;
  position: relative;
  z-index: 3;
}

.create-section {
  padding: 24rpx 30rpx;
}

.create-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fbff 100%);
  border-radius: 20rpx;
  padding: 32rpx;
  box-shadow: 0 6rpx 24rpx rgba(184, 212, 255, 0.3);
  border: 1rpx solid #d1e3ff;
}

.create-header {
  display: flex;
  align-items: center;
  margin-bottom: 12rpx;
}

.create-icon {
  width: 32rpx;
  height: 32rpx;
  margin-right: 16rpx;
}

.create-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #2c5282;
}

.create-desc {
  font-size: 24rpx;
  color: #5a7ca8;
  margin-bottom: 24rpx;
  line-height: 1.4;
}

.create-btn {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #b8d4ff 0%, #bcc4e8 100%);
  border-radius: 14rpx;
  padding: 20rpx 28rpx;
  box-shadow: 0 3rpx 12rpx rgba(139, 185, 255, 0.4);
}

.create-btn-text {
  font-size: 26rpx;
  color: #2c5282;
  font-weight: 600;
}

.create-arrow {
  width: 28rpx;
  height: 28rpx;
}

.list-section {
  background: transparent;
  margin-bottom: 16rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 30rpx 20rpx;
}

.section-title-wrapper {
  display: flex;
  align-items: center;
}

.section-icon {
  width: 36rpx;
  height: 36rpx;
  margin-right: 12rpx;
  opacity: 0.8;
}

.section-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #2c5282;
}

.section-count {
  font-size: 24rpx;
  color: #5a7ca8;
  background: rgba(184, 212, 255, 0.5);
  padding: 6rpx 14rpx;
  border-radius: 16rpx;
  font-weight: 500;
}

.route-list {
  padding: 0 30rpx;
}

.route-card {
  background: #ffffff;
  border-radius: 18rpx;
  padding: 28rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 3rpx 18rpx rgba(184, 212, 255, 0.3);
  border: 1rpx solid #e1edff;
  transition: all 0.3s ease;
}

.route-card:active {
  transform: translateY(2rpx);
  box-shadow: 0 2rpx 10rpx rgba(184, 212, 255, 0.4);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20rpx;
}

.route-basic {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.route-name {
  font-size: 32rpx;
  font-weight: 700;
  color: #2c5282;
  display: block;
  margin-bottom: 10rpx;
  line-height: 1.3;
  flex: 1;
}

.route-duration-badge {
  background: linear-gradient(135deg, #b8d4ff 0%, #8bb9ff 100%);
  padding: 6rpx 14rpx;
  border-radius: 14rpx;
  box-shadow: 0 2rpx 6rpx rgba(139, 185, 255, 0.3);
}

.duration-text {
  font-size: 20rpx;
  color: #2c5282;
  font-weight: 600;
}

.route-info {
  margin-bottom: 16rpx;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10rpx;
}

.info-item {
  display: flex;
  align-items: center;
  flex: 1;
}

.info-row:first-child .info-item {
  flex: none;
  width: 100%;
}

.info-icon {
  width: 26rpx;
  height: 26rpx;
  margin-right: 12rpx;
  opacity: 0.6;
}

.info-text {
  font-size: 24rpx;
  color: #5a7ca8;
  line-height: 1.4;
}

.route-desc {
  margin-bottom: 16rpx;
  padding: 16rpx;
  background: #f8fbff;
  border-radius: 10rpx;
  border-left: 3rpx solid #b8d4ff;
}

.desc-text {
  font-size: 24rpx;
  color: #5a7ca8;
  line-height: 1.4;
}

.route-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  margin-bottom: 20rpx;
}

.tag {
  background: rgba(184, 212, 255, 0.3);
  padding: 6rpx 14rpx;
  border-radius: 14rpx;
  font-size: 20rpx;
  color: #2c5282;
  font-weight: 500;
  border: 1rpx solid rgba(184, 212, 255, 0.5);
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16rpx;
  border-top: 1rpx solid #e1edff;
}

.route-meta {
  flex: 1;
}

.meta-text {
  font-size: 22rpx;
  color: #a0bcd8;
}

.route-actions {
  display: flex;
  gap: 12rpx;
}

.action-btn {
  display: flex;
  align-items: center;
  padding: 10rpx 16rpx;
  border-radius: 10rpx;
  transition: all 0.3s ease;
}

.action-btn.view-map {
  background: rgba(184, 212, 255, 0.3);
  border: 1rpx solid #b8d4ff;
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
  width: 24rpx;
  height: 24rpx;
  margin-right: 8rpx;
}

.action-btn.view-map .action-icon,
.action-btn.edit .action-icon {
  opacity: 0.8;
}

.action-btn.delete .action-icon {
  opacity: 0.8;
}

.action-text {
  font-size: 22rpx;
  font-weight: 500;
}

.action-btn.view-map .action-text,
.action-btn.edit .action-text {
  color: #2c5282;
}

.action-btn.delete .action-text {
  color: #ff6b6b;
}

.empty-state {
  background: transparent;
  padding: 100rpx 60rpx;
}

.empty-content {
  text-align: center;
  background: #ffffff;
  padding: 60rpx 40rpx;
  border-radius: 20rpx;
  box-shadow: 0 3rpx 18rpx rgba(184, 212, 255, 0.3);
  border: 1rpx solid #e1edff;
}

.empty-icon {
  width: 140rpx;
  height: 140rpx;
  margin-bottom: 24rpx;
  opacity: 0.5;
}

.empty-title {
  font-size: 30rpx;
  color: #2c5282;
  display: block;
  margin-bottom: 12rpx;
  font-weight: 600;
}

.empty-desc {
  font-size: 24rpx;
  color: #5a7ca8;
  display: block;
  margin-bottom: 32rpx;
  line-height: 1.4;
}

.empty-btn {
  background: linear-gradient(135deg, #b8d4ff 0%, #8bb9ff 100%);
  border-radius: 14rpx;
  padding: 20rpx 40rpx;
  display: inline-block;
  box-shadow: 0 3rpx 12rpx rgba(139, 185, 255, 0.4);
}

.empty-btn-text {
  font-size: 26rpx;
  color: #2c5282;
  font-weight: 600;
}

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
  padding: 32rpx;
  border-radius: 18rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 6rpx 24rpx rgba(184, 212, 255, 0.4);
  border: 1rpx solid #e1edff;
}

.loading-icon {
  width: 70rpx;
  height: 70rpx;
  margin-bottom: 16rpx;
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 26rpx;
  color: #5a7ca8;
  font-weight: 500;
}

.safe-area {
  height: env(safe-area-inset-bottom);
  background: #f0f7ff;
}
</style>