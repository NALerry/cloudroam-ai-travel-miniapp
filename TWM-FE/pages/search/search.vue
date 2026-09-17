<template>
  <view class="search-page">
    <!-- 搜索栏 -->
    <view class="search-header">
      <view class="search-box">
        <uni-icons type="search" size="18" color="#999"></uni-icons>
        <input 
          class="search-input" 
          v-model="searchKeyword"
          placeholder="搜索目的地、攻略或景点"
          focus
          @confirm="onSearch"
        />
        <view class="search-cancel" @tap="goBack" v-if="searchKeyword">
          <text>取消</text>
        </view>
      </view>
    </view>

    <!-- 搜索内容 -->
    <scroll-view class="search-content" scroll-y v-if="!searchKeyword">
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
            @tap="onHistoryTagTap(item)"
          >
            <text>{{ item }}</text>
          </view>
        </view>
      </view>

      <!-- 热门推荐 -->
      <view class="search-section">
        <view class="section-header">
          <text class="section-title">热门推荐</text>
        </view>
        <view class="tags-container">
          <view 
            class="search-tag hot" 
            v-for="item in hotSearches" 
            :key="item.keyword"
            @tap="onHotSearchTap(item)"
          >
            <text>{{ item.keyword }}</text>
            <text class="hot-icon" v-if="item.hot">热</text>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 搜索结果 -->
    <view class="search-results" v-else>
      <!-- 搜索结果列表 -->
      <view class="result-list">
        <view 
          class="result-item" 
          v-for="item in searchResults" 
          :key="item.id"
          @tap="onResultItemTap(item)"
        >
          <text class="result-title">{{ item.title }}</text>
          <text class="result-desc">{{ item.desc }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      searchKeyword: '',
      searchHistory: ['北京', '上海迪士尼', '成都火锅', '西安兵马俑'],
      hotSearches: [
        { keyword: '三亚海滩', hot: true },
        { keyword: '重庆洪崖洞', hot: true },
        { keyword: '厦门鼓浪屿', hot: false },
        { keyword: '桂林山水', hot: false },
        { keyword: '丽江古城', hot: true },
        { keyword: '西藏布达拉宫', hot: false }
      ],
      searchResults: []
    }
  },
  watch: {
    searchKeyword(newVal) {
      if (newVal) {
        this.search(newVal)
      } else {
        this.searchResults = []
      }
    }
  },
  methods: {
    onSearch() {
      if (!this.searchKeyword.trim()) return
      
      this.addToHistory(this.searchKeyword)
      this.navigateToResult()
    },
    
    onHistoryTagTap(keyword) {
      this.searchKeyword = keyword
      this.onSearch()
    },
    
    onHotSearchTap(item) {
      this.searchKeyword = item.keyword
      this.onSearch()
    },
    
    onResultItemTap(item) {
      uni.navigateTo({
        url: `/pages/detail/detail?id=${item.id}`
      })
    },
    
    addToHistory(keyword) {
      const index = this.searchHistory.indexOf(keyword)
      if (index > -1) {
        this.searchHistory.splice(index, 1)
      }
      this.searchHistory.unshift(keyword)
      
      // 保持最多10条历史记录
      if (this.searchHistory.length > 10) {
        this.searchHistory = this.searchHistory.slice(0, 10)
      }
      
      // 保存到本地存储
      uni.setStorageSync('search_history', this.searchHistory)
    },
    
    clearHistory() {
      uni.showModal({
        title: '提示',
        content: '确定清除所有历史记录吗？',
        success: (res) => {
          if (res.confirm) {
            this.searchHistory = []
            uni.removeStorageSync('search_history')
          }
        }
      })
    },
    
    async search(keyword) {
      // 模拟搜索API调用
      try {
        // 实际项目中调用搜索接口
        // const response = await uni.request({
        //   url: 'https://your-api.com/search',
        //   data: { keyword }
        // })
        
        // 模拟数据
        await new Promise(resolve => setTimeout(resolve, 500))
        
        this.searchResults = [
          { id: 1, title: `${keyword}旅游攻略`, desc: '最全的旅行指南和注意事项' },
          { id: 2, title: `${keyword}热门景点`, desc: '必去的十大景点推荐' },
          { id: 3, title: `${keyword}美食推荐`, desc: '当地特色美食和餐厅' },
          { id: 4, title: `${keyword}住宿指南`, desc: '高性价比酒店和民宿' }
        ]
      } catch (error) {
        console.error('搜索失败:', error)
      }
    },
    
    navigateToResult() {
      uni.navigateTo({
        url: `/pages/search/result?keyword=${encodeURIComponent(this.searchKeyword)}`
      })
    },
    
    goBack() {
      uni.navigateBack()
    }
  }
}
</script>

<style scoped>
.search-page {
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

.search-tag.hot {
  position: relative;
  padding-right: 60rpx;
}

.hot-icon {
  position: absolute;
  right: 8rpx;
  top: 50%;
  transform: translateY(-50%);
  background: #FF6A00;
  color: #fff;
  font-size: 20rpx;
  padding: 4rpx 8rpx;
  border-radius: 20rpx;
}

.search-results {
  padding: 0 30rpx;
}

.result-item {
  padding: 30rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.result-title {
  font-size: 32rpx;
  color: #333;
  display: block;
  margin-bottom: 10rpx;
}

.result-desc {
  font-size: 26rpx;
  color: #999;
}
</style>