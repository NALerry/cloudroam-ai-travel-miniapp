<template>
  <view class="map-search-page">
    <!-- 搜索栏 -->
    <view class="search-header">
      <view class="search-box">
        <uni-icons type="search" size="18" color="#999"></uni-icons>
        <input 
          class="search-input" 
          v-model="searchKeyword"
          placeholder="搜索地点或景点"
          focus
          @confirm="onSearch"
        />
        <view class="search-cancel" @tap="goBack">
          <text>取消</text>
        </view>
      </view>
    </view>

    <!-- 搜索内容 -->
    <scroll-view class="search-content" scroll-y>
      <!-- 历史搜索 -->
      <view class="search-section" v-if="searchHistory.length > 0">
        <view class="section-header">
          <text class="section-title">历史搜索</text>
          <view class="section-action" @tap="clearHistory">
            <uni-icons type="trash" size="16" color="#999"></uni-icons>
          </view>
        </view>
        <view class="tags-container">
          <view 
            class="search-tag" 
            v-for="item in searchHistory" 
            :key="item"
            @tap="onHistoryTap(item)"
          >
            <text>{{ item }}</text>
          </view>
        </view>
      </view>

      <!-- 热门地点 -->
      <view class="search-section">
        <view class="section-header">
          <text class="section-title">热门地点</text>
        </view>
        <view class="location-list">
          <view 
            class="location-item" 
            v-for="item in hotLocations" 
            :key="item.id"
            @tap="onLocationTap(item)"
          >
            <view class="location-info">
              <text class="location-name">{{ item.name }}</text>
              <text class="location-address">{{ item.address }}</text>
              <text class="location-distance">{{ item.distance }}</text>
            </view>
            <uni-icons type="location" size="20" color="#FF6A00"></uni-icons>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      searchKeyword: '',
      searchHistory: ['故宫', '天安门', '颐和园', '王府井', '南锣鼓巷'],
      hotLocations: [
        { id: 1, name: '故宫博物院', address: '北京市东城区景山前街4号', distance: '1.2km' },
        { id: 2, name: '天安门广场', address: '北京市东城区东长安街', distance: '800m' },
        { id: 3, name: '王府井大街', address: '北京市东城区王府井大街', distance: '1.5km' },
        { id: 4, name: '南锣鼓巷', address: '北京市东城区南锣鼓巷', distance: '2.3km' },
        { id: 5, name: '颐和园', address: '北京市海淀区新建宫门路19号', distance: '15km' }
      ]
    }
  },
  methods: {
    onSearch() {
      if (!this.searchKeyword.trim()) return
      
      this.addToHistory(this.searchKeyword)
      this.navigateBackWithResult()
    },
    
    onHistoryTap(keyword) {
      this.searchKeyword = keyword
      this.navigateBackWithResult()
    },
    
    onLocationTap(location) {
      // 返回地图页面并定位到选择的地点
      const pages = getCurrentPages()
      const prevPage = pages[pages.length - 2]
      
      prevPage.$vm.mapCenter = {
        latitude: this.getLocationLatLng(location.name).lat,
        longitude: this.getLocationLatLng(location.name).lng
      }
      
      prevPage.$vm.addSearchMarker({
        title: location.name,
        location: {
          lat: this.getLocationLatLng(location.name).lat,
          lng: this.getLocationLatLng(location.name).lng
        }
      })
      
      uni.navigateBack()
    },
    
    addToHistory(keyword) {
      const index = this.searchHistory.indexOf(keyword)
      if (index > -1) {
        this.searchHistory.splice(index, 1)
      }
      this.searchHistory.unshift(keyword)
      
      if (this.searchHistory.length > 10) {
        this.searchHistory = this.searchHistory.slice(0, 10)
      }
      
      uni.setStorageSync('map_search_history', this.searchHistory)
    },
    
    clearHistory() {
      uni.showModal({
        title: '提示',
        content: '确定清除所有历史记录吗？',
        success: (res) => {
          if (res.confirm) {
            this.searchHistory = []
            uni.removeStorageSync('map_search_history')
          }
        }
      })
    },
    
    navigateBackWithResult() {
      const pages = getCurrentPages()
      const prevPage = pages[pages.length - 2]
      
      if (prevPage) {
        prevPage.$vm.searchLocation(this.searchKeyword)
      }
      
      uni.navigateBack()
    },
    
    getLocationLatLng(name) {
      // 模拟地点坐标
      const locationMap = {
        '故宫博物院': { lat: 39.915, lng: 116.397 },
        '天安门广场': { lat: 39.908, lng: 116.397 },
        '王府井大街': { lat: 39.904, lng: 116.391 },
        '南锣鼓巷': { lat: 39.939, lng: 116.401 },
        '颐和园': { lat: 39.999, lng: 116.273 }
      }
      return locationMap[name] || { lat: 39.909, lng: 116.397 }
    },
    
    goBack() {
      uni.navigateBack()
    }
  }
}
</script>

<style scoped>
.map-search-page {
  height: 100vh;
  background: #fff;
}

.search-header {
  padding: 20rpx 30rpx;
  border-bottom: 1rpx solid #eee;
}

.search-box {
  display: flex;
  align-items: center;
  background: #f5f5f5;
  border-radius: 40rpx;
  padding: 20rpx 30rpx;
}

.search-input {
  flex: 1;
  margin-left: 20rpx;
  font-size: 28rpx;
}

.search-cancel {
  margin-left: 20rpx;
  font-size: 28rpx;
  color: #666;
}

.search-content {
  height: calc(100vh - 120rpx);
  padding: 0 30rpx;
}

.search-section {
  margin-top: 40rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
}

.section-action {
  padding: 10rpx;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
}

.search-tag {
  padding: 16rpx 32rpx;
  background: #f5f5f5;
  border-radius: 40rpx;
  font-size: 26rpx;
  color: #666;
}

.location-list {
  display: flex;
  flex-direction: column;
  gap: 30rpx;
}

.location-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 30rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.location-info {
  flex: 1;
}

.location-name {
  font-size: 30rpx;
  color: #333;
  display: block;
  margin-bottom: 8rpx;
}

.location-address {
  font-size: 26rpx;
  color: #999;
  display: block;
  margin-bottom: 8rpx;
}

.location-distance {
  font-size: 24rpx;
  color: #FF6A00;
}
</style>