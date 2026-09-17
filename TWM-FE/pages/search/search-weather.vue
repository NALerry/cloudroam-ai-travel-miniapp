<template>
  <view class="search-weather-page">
    <!-- 搜索栏 -->
    <view class="search-header">
      <view class="search-box">
        <view class="search-input-container">
          <uni-icons type="search" size="18" color="#999"></uni-icons>
          <input 
            class="search-input" 
            v-model="searchKeyword"
            placeholder="搜索城市名称"
            focus
            @confirm="onSearch"
          />
          <view class="search-clear" v-if="searchKeyword" @tap="clearKeyword">
            <uni-icons type="clear" size="16" color="#999"></uni-icons>
          </view>
        </view>
        <view class="search-cancel" @tap="goBack">
          <text>取消</text>
        </view>
      </view>
    </view>

    <!-- 搜索内容 -->
    <view class="search-content">
      <!-- 搜索结果 -->
      <scroll-view class="search-results" scroll-y v-if="searchKeyword && searchResults.length > 0">
        <view class="results-section">
          <view class="section-title">搜索结果</view>
          <view class="city-list">
            <view 
              class="city-item" 
              v-for="city in searchResults" 
              :key="city.id"
              @tap="selectCity(city)"
            >
              <view class="city-info">
                <text class="city-name">{{ city.name }}</text>
                <text class="city-desc">{{ city.province }} · {{ city.country }}</text>
              </view>
              <view class="city-weather">
                <text class="city-temp">{{ city.temperature }}°</text>
                <text class="city-weather-desc">{{ city.weather }}</text>
              </view>
            </view>
          </view>
        </view>
      </scroll-view>

      <!-- 无搜索结果 -->
      <view class="empty-results" v-else-if="searchKeyword && searchResults.length === 0">
        <image class="empty-icon" src="/static/search-empty.png" mode="aspectFit"></image>
        <text class="empty-text">未找到相关城市</text>
        <text class="empty-desc">请检查城市名称是否正确</text>
      </view>

      <!-- 默认状态：热门城市 -->
      <scroll-view class="default-content" scroll-y v-else>
        <view class="search-section">
          <view class="section-header">
            <text class="section-title">热门城市</text>
          </view>
          <view class="hot-cities">
            <view 
              class="city-tag" 
              v-for="city in hotCities" 
              :key="city.id"
              @tap="selectHotCity(city)"
            >
              <text>{{ city.name }}</text>
            </view>
          </view>
        </view>

        <!-- 最近访问 -->
        <view class="search-section" v-if="recentCities.length > 0">
          <view class="section-header">
            <text class="section-title">最近访问</text>
            <view class="section-action" @tap="clearRecentCities">
              <uni-icons type="trash" size="16" color="#999"></uni-icons>
            </view>
          </view>
          <view class="recent-cities">
            <view 
              class="recent-city" 
              v-for="city in recentCities" 
              :key="city.id"
              @tap="selectRecentCity(city)"
            >
              <uni-icons type="location" size="16" color="#FF6A00"></uni-icons>
              <text class="recent-city-name">{{ city.name }}</text>
            </view>
          </view>
        </view>
      </scroll-view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      searchKeyword: '',
      searchResults: [],
      hotCities: [
        { id: 1, name: '北京', province: '北京', country: '中国' },
        { id: 2, name: '上海', province: '上海', country: '中国' },
        { id: 3, name: '广州', province: '广东', country: '中国' },
        { id: 4, name: '深圳', province: '广东', country: '中国' },
        { id: 5, name: '杭州', province: '浙江', country: '中国' },
        { id: 6, name: '成都', province: '四川', country: '中国' },
        { id: 7, name: '西安', province: '陕西', country: '中国' },
        { id: 8, name: '南京', province: '江苏', country: '中国' }
      ],
      recentCities: []
    }
  },
  onLoad() {
    this.loadRecentCities()
  },
  watch: {
    searchKeyword(newVal) {
      if (newVal.trim()) {
        this.searchCities(newVal.trim())
      } else {
        this.searchResults = []
      }
    }
  },
  methods: {
    // 搜索城市
    async searchCities(keyword) {
      // 模拟搜索API调用
      try {
        // 模拟网络延迟
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // 模拟搜索结果
        this.searchResults = [
          {
            id: 101,
            name: `${keyword}市`,
            province: `${keyword}省`,
            country: '中国',
            temperature: Math.floor(Math.random() * 15) + 15,
            weather: ['晴', '多云', '阴', '小雨'][Math.floor(Math.random() * 4)]
          },
          {
            id: 102,
            name: `${keyword}县`,
            province: `${keyword}省`,
            country: '中国',
            temperature: Math.floor(Math.random() * 15) + 15,
            weather: ['晴', '多云', '阴', '小雨'][Math.floor(Math.random() * 4)]
          }
        ]
      } catch (error) {
        console.error('搜索失败:', error)
      }
    },
    
    // 选择城市
    selectCity(city) {
      this.addToRecentCities(city)
      
      // 返回天气页面并传递选择的城市
      const eventChannel = this.getOpenerEventChannel()
      eventChannel.emit('weatherCitySelected', {
        city: city.name,
        fromSearch: true
      })
      
      uni.navigateBack()
    },
    
    // 选择热门城市
    selectHotCity(city) {
      this.searchKeyword = city.name
      this.selectCity(city)
    },
    
    // 选择最近访问城市
    selectRecentCity(city) {
      this.selectCity(city)
    },
    
    // 添加到最近访问
    addToRecentCities(city) {
      // 移除重复项
      const index = this.recentCities.findIndex(item => item.id === city.id)
      if (index > -1) {
        this.recentCities.splice(index, 1)
      }
      
      // 添加到开头
      this.recentCities.unshift(city)
      
      // 限制数量
      if (this.recentCities.length > 5) {
        this.recentCities = this.recentCities.slice(0, 5)
      }
      
      // 保存到本地存储
      try {
        uni.setStorageSync('weather_recent_cities', this.recentCities)
      } catch (e) {
        console.log('保存最近城市失败:', e)
      }
    },
    
    // 加载最近访问城市
    loadRecentCities() {
      try {
        const cities = uni.getStorageSync('weather_recent_cities') || []
        this.recentCities = cities
      } catch (e) {
        console.log('加载最近城市失败:', e)
      }
    },
    
    // 清除最近访问城市
    clearRecentCities() {
      uni.showModal({
        title: '提示',
        content: '确定清除所有最近访问记录吗？',
        success: (res) => {
          if (res.confirm) {
            this.recentCities = []
            try {
              uni.removeStorageSync('weather_recent_cities')
            } catch (e) {
              console.log('清除最近城市失败:', e)
            }
          }
        }
      })
    },
    
    // 搜索确认
    onSearch() {
      if (this.searchKeyword.trim()) {
        this.searchCities(this.searchKeyword.trim())
      }
    },
    
    // 清除关键词
    clearKeyword() {
      this.searchKeyword = ''
      this.searchResults = []
    },
    
    // 返回上一页
    goBack() {
      uni.navigateBack()
    }
  }
}
</script>

<style scoped>
.search-weather-page {
  height: 100vh;
  background: #fff;
  display: flex;
  flex-direction: column;
}

.search-header {
  padding: 20rpx 30rpx;
  border-bottom: 1rpx solid #eee;
  background: #fff;
  position: sticky;
  top: 0;
  z-index: 10;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.search-input-container {
  flex: 1;
  display: flex;
  align-items: center;
  background: #f5f5f5;
  border-radius: 40rpx;
  padding: 20rpx 30rpx;
}

.search-input {
  flex: 1;
  margin: 0 20rpx;
  font-size: 28rpx;
  height: 40rpx;
  line-height: 40rpx;
}

.search-clear {
  padding: 8rpx;
}

.search-cancel {
  font-size: 28rpx;
  color: #666;
}

.search-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.search-results,
.default-content {
  flex: 1;
  padding: 0 30rpx;
}

.results-section {
  padding: 30rpx 0;
}

.section-title {
  font-size: 28rpx;
  color: #999;
  margin-bottom: 24rpx;
  display: block;
}

.city-list {
  background: #fff;
  border-radius: 16rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.06);
}

.city-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.city-item:last-child {
  border-bottom: none;
}

.city-info {
  flex: 1;
}

.city-name {
  font-size: 32rpx;
  color: #333;
  display: block;
  margin-bottom: 8rpx;
  font-weight: 500;
}

.city-desc {
  font-size: 24rpx;
  color: #999;
}

.city-weather {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.city-temp {
  font-size: 32rpx;
  color: #FF6A00;
  font-weight: 500;
  margin-bottom: 4rpx;
}

.city-weather-desc {
  font-size: 24rpx;
  color: #666;
}

.empty-results {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx 0;
}

.empty-icon {
  width: 200rpx;
  height: 200rpx;
  margin-bottom: 40rpx;
  opacity: 0.5;
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

.search-section {
  margin-top: 40rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.section-action {
  padding: 10rpx;
}

.hot-cities {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
}

.city-tag {
  padding: 20rpx 32rpx;
  background: #f5f5f5;
  border-radius: 40rpx;
  font-size: 28rpx;
  color: #333;
}

.recent-cities {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.recent-city {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 24rpx;
  background: #f8f8f8;
  border-radius: 12rpx;
}

.recent-city-name {
  font-size: 28rpx;
  color: #333;
}
</style>