<template>
  <view class="accommodation-page">
    <!-- 顶部导航栏 -->
    <view class="nav-bar">
      <view 
        class="nav-item" 
        :class="{ active: currentTab === 'hotel' }"
        @tap="switchTab('hotel')"
      >
        <text class="nav-text">酒店</text>
      </view>
      <view 
        class="nav-item" 
        :class="{ active: currentTab === 'bnb' }"
        @tap="switchTab('bnb')"
      >
        <text class="nav-text">民宿</text>
      </view>
    </view>

    <!-- 内容区域 -->
    <view class="content-section">
      <!-- 酒店内容 -->
      <view class="tab-content" v-if="currentTab === 'hotel'">
        <scroll-view class="content-scroll" scroll-y>
          <!-- 搜索区域 -->
          <view class="search-box">
            <view class="search-input">
              <image class="search-icon" src="/static/icons/general/search1.png"></image>
              <input 
                type="text" 
                placeholder="搜索酒店名称或位置" 
                v-model="hotelKeyword"
                @confirm="searchHotel"
              />
            </view>
          </view>
          
          <!-- 分类导航 -->
          <view class="category-section">
            <scroll-view class="category-scroll" scroll-x :show-scrollbar="false">
              <view 
                class="category-item" 
                v-for="category in categories" 
                :key="category.id"
                :class="{ active: activeCategory === category.id }"
                @tap="onCategoryChange(category.id)"
              >
                <image class="category-icon" :src="category.icon" mode="aspectFit"></image>
                <text class="category-name">{{ category.name }}</text>
              </view>
            </scroll-view>
          </view>

          <!-- 筛选条件 -->
          <view class="filter-section">
            <view class="filter-row">
              <view 
                class="filter-item" 
                v-for="filter in filters" 
                :key="filter.type"
                :class="{ active: activeFilter === filter.type }"
                @tap="onFilterChange(filter.type)"
              >
                <text>{{ filter.name }}</text>
                <image class="filter-arrow" src="/static/icons/general/arrow-down.png" mode="aspectFit"></image>
              </view>
            </view>
          </view>
          
          <!-- 推荐酒店 -->
          <view class="recommend-section">
            <view class="section-header">
              <text class="section-title">推荐酒店</text>
              <text class="section-more" @tap="navigateToHotelPage">查看更多</text>
            </view>
            <view class="recommend-list">
              <view 
                class="recommend-card" 
                v-for="item in recommendedHotels" 
                :key="item.id"
                @tap="viewHotelDetail(item)"
              >
                <view class="hotel-image">
                  <image :src="item.image" mode="aspectFill"></image>
                  <view class="type-tag">{{ item.type }}</view>
                  <view class="rating-tag">
                    <text class="rating-star">★</text>
                    <text class="rating-score">{{ item.rating }}</text>
                  </view>
                </view>
                <view class="hotel-info">
                  <view class="hotel-header">
                    <text class="hotel-name">{{ item.name }}</text>
                    <text class="hotel-price">{{ item.price }}</text>
                  </view>
                  <text class="hotel-desc">{{ item.description }}</text>
                  <view class="hotel-tags">
                    <text 
                      class="tag" 
                      v-for="(tag, index) in item.tags" 
                      :key="index"
                    >{{ tag }}</text>
                  </view>
                  <view class="hotel-location">
                    <image class="location-icon" src="/static/icons/general/location.png"></image>
                    <text class="location-text">{{ item.location }}</text>
                    <text class="distance">{{ item.distance }}</text>
                  </view>
                </view>
              </view>
            </view>
          </view>

          <!-- 热门酒店 -->
          <view class="hot-section">
            <view class="section-header">
              <text class="section-title">热门酒店</text>
              <text class="section-more" @tap="navigateToHotelPage">查看更多</text>
            </view>
            <view class="hot-list">
              <view 
                class="hot-card" 
                v-for="item in hotHotels" 
                :key="item.id"
                @tap="viewHotelDetail(item)"
              >
                <view class="hot-image">
                  <image :src="item.image" mode="aspectFill"></image>
                  <view class="hot-badge">热门</view>
                </view>
                <view class="hot-info">
                  <text class="hot-name">{{ item.name }}</text>
                  <view class="hot-rating">
                    <text class="rating-star">★</text>
                    <text class="rating-score">{{ item.rating }}</text>
                  </view>
                  <text class="hot-price">{{ item.price }}</text>
                </view>
              </view>
            </view>
          </view>
        </scroll-view>
      </view>

      <!-- 民宿内容 -->
      <view class="tab-content" v-if="currentTab === 'bnb'">
        <scroll-view class="content-scroll" scroll-y>
          <!-- 搜索区域 -->
          <view class="search-box">
            <view class="search-input">
              <image class="search-icon" src="/static/icons/general/search1.png"></image>
              <input 
                type="text" 
                placeholder="搜索民宿名称或特色" 
                v-model="bnbKeyword"
                @confirm="searchBnb"
              />
            </view>
          </view>

          <!-- 民宿筛选条件 -->
          <view class="filter-section">
            <view class="filter-row">
              <view 
                class="filter-item" 
                v-for="filter in bnbFilters" 
                :key="filter.type"
                :class="{ active: activeBnbFilter === filter.type }"
                @tap="onBnbFilterChange(filter.type)"
              >
                <text>{{ filter.name }}</text>
                <image class="filter-arrow" src="/static/icons/general/arrow-down.png" mode="aspectFit"></image>
              </view>
            </view>
          </view>
          
          <!-- 特色民宿 -->
          <view class="feature-section">
            <view class="section-header">
              <text class="section-title">特色民宿</text>
            </view>
            <view class="bnb-list">
              <view 
                class="bnb-card" 
                v-for="item in filteredBnbs" 
                :key="item.id"
                @tap="viewBnbDetail(item)"
              >
                <view class="bnb-image">
                  <image :src="item.image" mode="aspectFill"></image>
                  <view class="style-tag" :class="item.style">
                    {{ item.style === 'traditional' ? '传统' : item.style === 'modern' ? '现代' : '特色' }}
                  </view>
                  <view class="rating-tag">
                    <text class="rating-star">★</text>
                    <text class="rating-score">{{ item.rating }}</text>
                  </view>
                </view>
                <view class="bnb-info">
                  <view class="bnb-header">
                    <text class="bnb-name">{{ item.name }}</text>
                    <text class="bnb-price">{{ item.price }}</text>
                  </view>
                  <text class="bnb-desc">{{ item.description }}</text>
                  <view class="bnb-tags">
                    <text 
                      class="tag" 
                      v-for="(tag, index) in item.tags" 
                      :key="index"
                    >{{ tag }}</text>
                  </view>
                  <view class="bnb-location">
                    <image class="location-icon" src="/static/icons/general/location.png"></image>
                    <text class="location-text">{{ item.location }}</text>
                    <text class="distance">{{ item.distance }}</text>
                  </view>
                  <view class="bnb-features">
                    <text class="feature" v-for="(feature, index) in item.features" :key="index">
                      {{ feature }}
                    </text>
                  </view>
                </view>
              </view>
            </view>
          </view>
        </scroll-view>
      </view>
    </view>

    <!-- 底部操作栏 -->
    <view class="bottom-bar" v-if="currentTab === 'hotel'">
      <view class="bottom-btn primary" @tap="navigateToHotelPage">
        <text>查看全部酒店</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      currentTab: 'hotel', // 当前选中的标签
      hotelKeyword: '', // 酒店搜索关键词
      bnbKeyword: '', // 民宿搜索关键词
      activeCategory: 'all',
      activeFilter: 'all',
      activeBnbFilter: 'all',
      
      categories: [
        { id: 'all', name: '全部', icon: '/static/icons/accommodation/all.png' },
        { id: 'luxury', name: '豪华', icon: '/static/icons/accommodation/luxury.png' },
        { id: 'business', name: '商务', icon: '/static/icons/accommodation/business.png' },
        { id: 'budget', name: '经济', icon: '/static/icons/accommodation/budget.png' },
        { id: 'resort', name: '度假', icon: '/static/icons/accommodation/resort.png' }
      ],
      filters: [
        { type: 'all', name: '智能排序' },
        { type: 'distance', name: '距离最近' },
        { type: 'rating', name: '评分最高' },
        { type: 'price', name: '价格排序' }
      ],
      bnbFilters: [
        { type: 'all', name: '智能排序' },
        { type: 'distance', name: '距离最近' },
        { type: 'rating', name: '评分最高' },
        { type: 'popularity', name: '热门程度' }
      ],
      
      // 推荐酒店数据（精简版，用于预览）
      recommendedHotels: [
        {
          id: 1,
          name: '四季酒店',
          type: '豪华酒店',
          rating: 4.9,
          price: '￥1200起',
          description: '国际五星级酒店，提供顶级的服务和设施。',
          image: '/static/images/accommodation/four-seasons.jpg',
          location: '北京市朝阳区CBD',
          distance: '0.8km',
          tags: ['五星级', '豪华', '市中心']
        },
        {
          id: 2,
          name: '希尔顿酒店',
          type: '商务酒店',
          rating: 4.7,
          price: '￥800起',
          description: '国际知名商务酒店，设施完善，服务专业。',
          image: '/static/images/accommodation/hilton.jpg',
          location: '上海市浦东新区陆家嘴',
          distance: '1.2km',
          tags: ['商务', '四星级', '交通便利']
        },
        {
          id: 3,
          name: '如家快捷酒店',
          type: '经济型',
          rating: 4.2,
          price: '￥200起',
          description: '全国连锁经济型酒店，干净舒适，性价比高。',
          image: '/static/images/accommodation/home-inn.jpg',
          location: '广州市天河区体育西路',
          distance: '2.1km',
          tags: ['经济', '连锁', '干净']
        }
      ],

      // 热门酒店数据
      hotHotels: [
        {
          id: 4,
          name: '万达文华酒店',
          type: '豪华酒店',
          rating: 4.8,
          price: '￥980起',
          image: '/static/images/accommodation/wanda.jpg',
          location: '杭州市西湖区'
        },
        {
          id: 5,
          name: '洲际酒店',
          type: '商务酒店',
          rating: 4.7,
          price: '￥850起',
          image: '/static/images/accommodation/intercontinental.jpg',
          location: '成都市高新区'
        },
        {
          id: 6,
          name: '喜来登酒店',
          type: '豪华酒店',
          rating: 4.6,
          price: '￥920起',
          image: '/static/images/accommodation/sheraton.jpg',
          location: '南京市鼓楼区'
        }
      ],
      
      // 民宿数据
      filteredBnbs: [
        {
          id: 1,
          name: '老北京四合院',
          image: '/static/images/accommodation/courtyard.jpg',
          rating: 4.9,
          price: '￥800起',
          description: '传统北京四合院改造的民宿，体验老北京生活。',
          style: 'traditional',
          location: '北京市东城区胡同',
          distance: '1.5km',
          tags: ['四合院', '传统', '文化体验'],
          features: ['独立院落', '传统家具', '茶室']
        },
        {
          id: 2,
          name: '海边悬崖民宿',
          image: '/static/images/accommodation/cliff-house.jpg',
          rating: 4.8,
          price: '￥1500起',
          description: '位于海边悬崖上的现代风格民宿，无敌海景。',
          style: 'modern',
          location: '青岛市崂山区海边',
          distance: '0.1km',
          tags: ['海景', '现代', '悬崖'],
          features: ['无边泳池', '海景露台', '私人厨师']
        },
        {
          id: 3,
          name: '丽江古城客栈',
          image: '/static/images/accommodation/lijiang-inn.jpg',
          rating: 4.7,
          price: '￥400起',
          description: '位于丽江古城内的纳西风格客栈，古色古香。',
          style: 'traditional',
          location: '丽江市古城区',
          distance: '0.3km',
          tags: ['古城', '纳西风格', '文艺'],
          features: ['庭院', '书吧', '茶室']
        }
      ]
    }
  },
  
  methods: {
    getCategoryName(categoryId) {
      const category = this.categories.find(cat => cat.id === categoryId);
      return category ? category.name : '';
    },
    
    // 切换标签
    switchTab(tab) {
      this.currentTab = tab
    },
    
    // 搜索酒店
    searchHotel() {
      // 跳转到酒店页面进行搜索
      this.navigateToHotelPage();
    },
    
    // 搜索民宿
    searchBnb() {
      uni.showToast({
        title: '搜索完成',
        icon: 'success'
      })
    },
    
    onCategoryChange(categoryId) {
      this.activeCategory = categoryId;
    },
    
    onFilterChange(filterType) {
      this.activeFilter = filterType;
    },
    
    onBnbFilterChange(filterType) {
      this.activeBnbFilter = filterType;
    },
    
    // 查看酒店详情
    viewHotelDetail(item) {
      uni.navigateTo({
        url: `/pages/hotel/hotel?hotelId=${item.id}`
      })
    },
    
    // 查看民宿详情
    viewBnbDetail(item) {
      uni.navigateTo({
        url: `/pages/accommodation/bnb-detail?id=${item.id}`
      })
    },

    // 跳转到酒店页面
    navigateToHotelPage() {
      uni.navigateTo({
        url: '/pages/hotel/hotel'
      })
    }
  },
  
  onLoad(options) {
    // 处理URL参数，设置默认标签页
    if (options.tab) {
      this.currentTab = options.tab;
    }
  }
}
</script>

<style scoped>
.accommodation-page {
  height: 100vh;
  background: linear-gradient(135deg, #f0f6ff 0%, #e8ecff 100%);
  display: flex;
  flex-direction: column;
}

/* 导航栏样式 */
.nav-bar {
  display: flex;
  background-color: #fff;
  border-bottom: 1rpx solid #e0e8ff;
  position: sticky;
  top: 0;
  z-index: 10;
  box-shadow: 0 2rpx 10rpx rgba(184, 212, 255, 0.2);
}

.nav-item {
  flex: 1;
  text-align: center;
  padding: 30rpx 0;
  position: relative;
  transition: all 0.3s ease;
}

.nav-text {
  font-size: 32rpx;
  color: #8a9bc1;
  font-weight: 500;
  transition: all 0.3s;
}

.nav-item.active .nav-text {
  color: #5a7bdb;
  font-weight: 600;
}

.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 80rpx;
  height: 6rpx;
  background: linear-gradient(90deg, #b8d4ff, #bcc4e8);
  border-radius: 3rpx;
  box-shadow: 0 2rpx 6rpx rgba(184, 212, 255, 0.5);
}

/* 内容区域样式 */
.content-section {
  flex: 1;
  overflow: hidden;
}

.tab-content {
  height: 100%;
}

.content-scroll {
  height: 100%;
}

/* 搜索框样式 */
.search-box {
  padding: 30rpx;
  background-color: #fff;
  border-bottom: 1rpx solid #e0e8ff;
}

.search-input {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #f5f9ff 0%, #edf2ff 100%);
  border: 1rpx solid #d0deff;
  border-radius: 50rpx;
  padding: 20rpx 30rpx;
  box-shadow: 0 4rpx 12rpx rgba(184, 212, 255, 0.2);
}

.search-icon {
  width: 36rpx;
  height: 36rpx;
  margin-right: 20rpx;
}

.search-input input {
  flex: 1;
  font-size: 28rpx;
  color: #5a7bdb;
  background: transparent;
}

.search-input input::placeholder {
  color: #8a9bc1;
}

/* 分类导航 */
.category-section {
  background: #fff;
  padding: 25rpx 30rpx;
  border-bottom: 1rpx solid #e0e8ff;
}

.category-scroll {
  white-space: nowrap;
}

.category-item {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  padding: 0 20rpx;
  transition: all 0.3s ease;
}

.category-item.active .category-icon {
  background: linear-gradient(135deg, #b8d4ff, #bcc4e8);
  transform: scale(1.1);
}

.category-item.active .category-name {
  color: #5a7bdb;
  font-weight: 600;
}

.category-icon {
  width: 80rpx;
  height: 80rpx;
  background: #f5f5f5;
  border-radius: 20rpx;
  padding: 15rpx;
  margin-bottom: 12rpx;
  transition: all 0.3s ease;
}

.category-name {
  font-size: 22rpx;
  color: #8a9bc1;
}

/* 筛选条件 */
.filter-section {
  background: #fff;
  padding: 20rpx 30rpx;
  border-bottom: 1rpx solid #e0e8ff;
}

.filter-row {
  display: flex;
  justify-content: space-around;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 26rpx;
  color: #8a9bc1;
  padding: 12rpx 20rpx;
  transition: all 0.3s ease;
  border-radius: 20rpx;
}

.filter-item.active {
  color: #5a7bdb;
  background: linear-gradient(135deg, #f0f7ff, #e8ecff);
}

.filter-arrow {
  width: 20rpx;
  height: 20rpx;
}

/* 分区标题 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  background: #fff;
}

.section-title {
  font-size: 36rpx;
  font-weight: 700;
  color: #3a5bc7;
  text-shadow: 0 2rpx 4rpx rgba(184, 212, 255, 0.3);
}

.section-more {
  font-size: 26rpx;
  color: #8a9bc1;
  transition: all 0.3s ease;
}

.section-more:active {
  color: #5a7bdb;
  transform: scale(0.95);
}

/* 推荐酒店样式 */
.recommend-section {
  background: #fff;
  margin-top: 20rpx;
}

.recommend-list {
  padding: 0 30rpx 30rpx;
}

.recommend-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fbff 100%);
  border-radius: 24rpx;
  overflow: hidden;
  margin-top: 20rpx;
  box-shadow: 0 6rpx 20rpx rgba(184, 212, 255, 0.3);
  border: 1rpx solid #e0e8ff;
  transition: all 0.3s ease;
}

.recommend-card:active {
  transform: translateY(4rpx);
  box-shadow: 0 2rpx 10rpx rgba(184, 212, 255, 0.2);
}

.hotel-image {
  position: relative;
  height: 280rpx;
}

.hotel-image image {
  width: 100%;
  height: 100%;
}

.type-tag {
  position: absolute;
  top: 20rpx;
  right: 20rpx;
  background: linear-gradient(135deg, #b8d4ff, #bcc4e8);
  color: #3a5bc7;
  padding: 10rpx 20rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
  font-weight: 600;
  box-shadow: 0 2rpx 8rpx rgba(184, 212, 255, 0.5);
}

.rating-tag {
  position: absolute;
  top: 20rpx;
  left: 20rpx;
  background: rgba(255, 255, 255, 0.9);
  color: #ff9500;
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
}

.rating-star {
  font-size: 24rpx;
  margin-right: 4rpx;
}

.hotel-info {
  padding: 25rpx;
}

.hotel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15rpx;
}

.hotel-name {
  font-size: 32rpx;
  font-weight: 700;
  color: #3a5bc7;
  text-shadow: 0 2rpx 4rpx rgba(184, 212, 255, 0.3);
}

.hotel-price {
  font-size: 26rpx;
  color: #ff6b6b;
  background: #fff0f0;
  padding: 8rpx 16rpx;
  border-radius: 16rpx;
  font-weight: 600;
}

.hotel-desc {
  font-size: 26rpx;
  color: #666;
  line-height: 1.5;
  margin-bottom: 15rpx;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}

.hotel-tags {
  display: flex;
  flex-wrap: wrap;
  margin-bottom: 15rpx;
}

.tag {
  background: linear-gradient(135deg, #b8d4ff, #bcc4e8);
  color: #3a5bc7;
  padding: 8rpx 16rpx;
  border-radius: 16rpx;
  font-size: 22rpx;
  margin-right: 12rpx;
  margin-bottom: 8rpx;
  font-weight: 500;
  box-shadow: 0 2rpx 6rpx rgba(184, 212, 255, 0.4);
}

.hotel-location {
  display: flex;
  align-items: center;
}

.location-icon {
  width: 24rpx;
  height: 24rpx;
  margin-right: 8rpx;
}

.location-text {
  font-size: 24rpx;
  color: #8a9bc1;
  flex: 1;
}

.distance {
  font-size: 22rpx;
  color: #5a7bdb;
  font-weight: 500;
}

/* 热门酒店样式 */
.hot-section {
  background: #fff;
  margin-top: 20rpx;
}

.hot-list {
  padding: 0 30rpx 30rpx;
  display: flex;
  overflow-x: auto;
  gap: 20rpx;
}

.hot-card {
  flex-shrink: 0;
  width: 300rpx;
  background: linear-gradient(135deg, #ffffff 0%, #f8fbff 100%);
  border-radius: 20rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 15rpx rgba(184, 212, 255, 0.3);
  border: 1rpx solid #e0e8ff;
}

.hot-image {
  position: relative;
  height: 200rpx;
}

.hot-image image {
  width: 100%;
  height: 100%;
}

.hot-badge {
  position: absolute;
  top: 15rpx;
  right: 15rpx;
  background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
  color: #fff;
  padding: 6rpx 12rpx;
  border-radius: 12rpx;
  font-size: 20rpx;
  font-weight: 600;
}

.hot-info {
  padding: 20rpx;
}

.hot-name {
  font-size: 28rpx;
  font-weight: 600;
  color: #3a5bc7;
  margin-bottom: 10rpx;
  display: block;
}

.hot-rating {
  display: flex;
  align-items: center;
  gap: 4rpx;
  color: #ff9500;
  font-size: 22rpx;
  margin-bottom: 10rpx;
}

.hot-price {
  font-size: 24rpx;
  color: #ff6b6b;
  font-weight: 600;
}

/* 民宿列表样式 */
.feature-section {
  background: #fff;
  margin-top: 20rpx;
}

.bnb-list {
  padding: 0 30rpx 30rpx;
}

.bnb-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fbff 100%);
  border-radius: 24rpx;
  overflow: hidden;
  margin-top: 20rpx;
  box-shadow: 0 6rpx 20rpx rgba(184, 212, 255, 0.3);
  border: 1rpx solid #e0e8ff;
  transition: all 0.3s ease;
}

.bnb-card:active {
  transform: translateY(4rpx);
  box-shadow: 0 2rpx 10rpx rgba(184, 212, 255, 0.2);
}

.bnb-image {
  position: relative;
  height: 280rpx;
}

.bnb-image image {
  width: 100%;
  height: 100%;
}

.style-tag {
  position: absolute;
  top: 20rpx;
  right: 20rpx;
  background: linear-gradient(135deg, #b8d4ff, #bcc4e8);
  color: #3a5bc7;
  padding: 10rpx 20rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
  font-weight: 600;
  box-shadow: 0 2rpx 8rpx rgba(184, 212, 255, 0.5);
}

.style-tag.traditional {
  background: linear-gradient(135deg, #ffb74d, #ff9800);
  color: #fff;
}

.style-tag.modern {
  background: linear-gradient(135deg, #4fc3f7, #0288d1);
  color: #fff;
}

.style-tag.feature {
  background: linear-gradient(135deg, #ba68c8, #8e24aa);
  color: #fff;
}

.bnb-info {
  padding: 25rpx;
}

.bnb-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15rpx;
}

.bnb-name {
  font-size: 32rpx;
  font-weight: 700;
  color: #3a5bc7;
  text-shadow: 0 2rpx 4rpx rgba(184, 212, 255, 0.3);
}

.bnb-price {
  font-size: 26rpx;
  color: #ff6b6b;
  background: #fff0f0;
  padding: 8rpx 16rpx;
  border-radius: 16rpx;
  font-weight: 600;
}

.bnb-desc {
  font-size: 26rpx;
  color: #666;
  line-height: 1.5;
  margin-bottom: 15rpx;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}

.bnb-tags {
  display: flex;
  flex-wrap: wrap;
  margin-bottom: 15rpx;
}

.bnb-location {
  display: flex;
  align-items: center;
  margin-bottom: 15rpx;
}

.bnb-features {
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx;
}

.feature {
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  color: #1565c0;
  padding: 6rpx 12rpx;
  border-radius: 12rpx;
  font-size: 20rpx;
  border: 1rpx solid #90caf9;
}

/* 底部操作栏 */
.bottom-bar {
  background: #fff;
  padding: 20rpx 30rpx;
  border-top: 1rpx solid #e0e8ff;
  box-shadow: 0 -2rpx 10rpx rgba(184, 212, 255, 0.1);
}

.bottom-btn {
  background: linear-gradient(135deg, #b8d4ff, #bcc4e8);
  color: #fff;
  text-align: center;
  padding: 25rpx;
  border-radius: 16rpx;
  font-size: 32rpx;
  font-weight: 600;
  transition: all 0.3s ease;
}

.bottom-btn:active {
  transform: scale(0.98);
  box-shadow: 0 2rpx 8rpx rgba(184, 212, 255, 0.4);
}

/* 添加一些动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.recommend-card, .bnb-card, .hot-card {
  animation: fadeIn 0.5s ease forwards;
}

/* 响应式设计 */
@media (max-width: 750rpx) {
  .recommend-list, .bnb-list, .hot-list {
    padding: 0 20rpx 20rpx;
  }
  
  .search-box {
    padding: 20rpx;
  }
  
  .hotel-info, .bnb-info {
    padding: 20rpx;
  }
  
  .hot-card {
    width: 280rpx;
  }
}
</style>