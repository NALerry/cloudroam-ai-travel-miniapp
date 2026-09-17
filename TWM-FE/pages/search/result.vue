<template>
  <view class="search-result-page">
    <!-- 搜索头部 -->
    <view class="search-header">
      <view class="search-box">
        <view class="search-input-container">
          <uni-icons type="search" size="18" color="#999"></uni-icons>
          <input 
            class="search-input" 
            v-model="searchKeyword"
            placeholder="搜索目的地、攻略或景点"
            @confirm="onSearch"
          />
        </view>
        <view class="search-cancel" @tap="goBack">
          <text>取消</text>
        </view>
      </view>
    </view>

    <!-- 搜索结果 -->
    <view class="result-content">
      <view class="result-header">
        <text class="result-count">找到 {{ searchResults.length }} 个结果</text>
        <text class="search-keyword">"{{ initialKeyword }}"</text>
      </view>

      <scroll-view class="result-list" scroll-y>
        <view 
          class="result-item" 
          v-for="item in searchResults" 
          :key="item.id"
          @tap="viewDetail(item)"
        >
          <view class="item-content">
            <text class="item-title">{{ item.title }}</text>
            <text class="item-desc">{{ item.desc }}</text>
            <view class="item-meta">
              <text class="item-type">{{ item.type }}</text>
              <text class="item-time">{{ item.time }}</text>
            </view>
          </view>
          <image class="item-image" :src="item.image" mode="aspectFill" v-if="item.image"></image>
        </view>
      </scroll-view>

      <!-- 加载更多 -->
      <view class="load-more" v-if="hasMore">
        <text class="load-text" @tap="loadMore">加载更多</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      searchKeyword: '',
      initialKeyword: '',
      searchResults: [],
      hasMore: false
    }
  },
  onLoad(options) {
    if (options.keyword) {
      this.searchKeyword = decodeURIComponent(options.keyword)
      this.initialKeyword = this.searchKeyword
      this.loadSearchResults(this.searchKeyword)
    }
  },
  methods: {
    onSearch() {
      if (!this.searchKeyword.trim()) return
      this.initialKeyword = this.searchKeyword
      this.loadSearchResults(this.searchKeyword)
    },
    
    async loadSearchResults(keyword) {
      uni.showLoading({
        title: '搜索中...'
      })
      
      try {
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // 模拟搜索结果数据
        this.searchResults = [
          {
            id: 1,
            title: `${keyword}旅游攻略`,
            desc: '最全的旅行指南和注意事项，包含交通、住宿、美食等实用信息',
            type: '攻略',
            time: '2024-01-15',
            image: '/static/search/strategy.jpg'
          },
          {
            id: 2,
            title: `${keyword}热门景点`,
            desc: '必去的十大景点推荐，详细介绍每个景点的特色和游玩时间',
            type: '景点',
            time: '2024-01-14',
            image: '/static/search/attraction.jpg'
          },
          {
            id: 3,
            title: `${keyword}美食推荐`,
            desc: '当地特色美食和餐厅推荐，包含价格区间和口味描述',
            type: '美食',
            time: '2024-01-13'
          },
          {
            id: 4,
            title: `${keyword}住宿指南`,
            desc: '高性价比酒店和民宿推荐，包含地理位置和设施介绍',
            type: '住宿',
            time: '2024-01-12',
            image: '/static/search/hotel.jpg'
          }
        ]
        
        this.hasMore = true
        uni.hideLoading()
      } catch (error) {
        uni.hideLoading()
        uni.showToast({
          title: '搜索失败',
          icon: 'none'
        })
      }
    },
    
    viewDetail(item) {
      uni.navigateTo({
        url: `/pages/detail/detail?id=${item.id}&title=${encodeURIComponent(item.title)}`
      })
    },
    
    loadMore() {
      // 加载更多结果的逻辑
      uni.showLoading({ title: '加载中...' })
      setTimeout(() => {
        // 模拟加载更多数据
        uni.hideLoading()
        uni.showToast({
          title: '没有更多结果了',
          icon: 'none'
        })
        this.hasMore = false
      }, 1000)
    },
    
    goBack() {
      uni.navigateBack()
    }
  }
}
</script>

<style scoped>
.search-result-page {
  height: 100vh;
  background: #f8f8f8;
  display: flex;
  flex-direction: column;
}

.search-header {
  background: #fff;
  padding: 20rpx 30rpx;
  border-bottom: 1rpx solid #eee;
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
  margin-left: 20rpx;
  font-size: 28rpx;
}

.search-cancel {
  font-size: 28rpx;
  color: #666;
}

.result-content {
  flex: 1;
  padding: 30rpx;
}

.result-header {
  margin-bottom: 30rpx;
}

.result-count {
  font-size: 28rpx;
  color: #666;
  display: block;
  margin-bottom: 8rpx;
}

.search-keyword {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
}

.result-list {
  height: calc(100vh - 300rpx);
}

.result-item {
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  display: flex;
  gap: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.06);
}

.item-content {
  flex: 1;
}

.item-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  display: block;
  margin-bottom: 16rpx;
  line-height: 1.4;
}

.item-desc {
  font-size: 26rpx;
  color: #666;
  line-height: 1.5;
  display: block;
  margin-bottom: 20rpx;
}

.item-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-type {
  font-size: 24rpx;
  color: #FF6A00;
  background: #FFF0E6;
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
}

.item-time {
  font-size: 22rpx;
  color: #999;
}

.item-image {
  width: 120rpx;
  height: 120rpx;
  border-radius: 12rpx;
  flex-shrink: 0;
}

.load-more {
  text-align: center;
  padding: 40rpx;
}

.load-text {
  font-size: 28rpx;
  color: #FF6A00;
}
</style>