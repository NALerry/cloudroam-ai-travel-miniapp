<template>
  <view class="ticket-page">
    <!-- 顶部导航栏（类似美食页） -->
    <view class="nav-bar">
      <view class="nav-item active">
        <text class="nav-text">景点门票</text>
      </view>
    </view>

    <!-- 搜索栏（类似美食页样式） -->
    <view class="search-section">
      <view class="search-box">
        <view class="search-input">
          <image class="search-icon" src="/static/icons/general/search1.png" mode="aspectFit"></image>
          <input 
            type="text" 
            placeholder="搜索景点名称" 
            v-model="searchKeyword"
            @confirm="onSearchConfirm"
            @input="onSearchInput"
          />
          <view class="search-cancel" v-if="searchKeyword" @tap="onSearchCancel">
            <text>取消</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 分类导航（文字胶囊样式） -->
    <view class="category-section" v-if="categories.length">
      <scroll-view class="category-scroll" scroll-x :show-scrollbar="false">
        <view 
          class="category-item" 
          v-for="category in categories" 
          :key="category.id"
          :class="{ active: activeCategory === category.id }"
          @tap="onCategoryChange(category.id)"
        >
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

    <!-- 景点列表 -->
    <view class="attraction-list">
      <scroll-view 
        class="list-scroll" 
        scroll-y 
        @scrolltolower="loadMore"
        :refresher-enabled="true"
        :refresher-triggered="refreshing"
        @refresherrefresh="onRefresh"
      >
        <view v-if="loading && attractionsAll.length === 0" class="loading-container">
          <text class="loading-text">正在获取附近景点...</text>
        </view>

        <view v-else-if="filteredAttractions.length === 0 && !loading" class="empty-container">
          <text class="empty-text">没有找到景点</text>
          <text class="empty-sub">尝试切换分类或搜索关键词</text>
        </view>

        <view 
          class="attraction-card" 
          v-for="attraction in filteredAttractions" 
          :key="attraction.id"
          @tap="viewAttractionDetail(attraction)"
        >
          <view class="attraction-info-full">
            <view class="attraction-header">
              <text class="attraction-name">{{ attraction.name }}</text>
              <view class="rating-tag" v-if="attraction.rating">
                <text class="rating-star">★</text>
                <text class="rating-score">{{ attraction.rating }}</text>
              </view>
              <view class="rating-tag" v-else>
                <text class="rating-score">暂无评分</text>
              </view>
            </view>
            
            <text class="attraction-desc" v-if="attraction.address">{{ attraction.address }}</text>
            
            <view class="attraction-tags">
              <text class="tag" v-for="tag in attraction.tags.slice(0, 3)" :key="tag">{{ tag }}</text>
            </view>
            
            <view class="attraction-location">
              <image class="location-icon" src="/static/icons/general/location.png" mode="aspectFit"></image>
              <text class="location-text">{{ attraction.address }}</text>
              <text class="distance">{{ attraction.distance }}</text>
            </view>

            <view class="attraction-info-row" v-if="attraction.openingHours">
              <text class="info-icon">🕒</text>
              <text class="info-text">{{ attraction.openingHours }}</text>
            </view>

            <view class="attraction-actions">
              <view class="nav-button navigation" @tap.stop="navigateToAttraction(attraction)">
                <text class="nav-icon">🗺️</text>
                <text class="nav-text">导航</text>
              </view>
              <view class="nav-button call" @tap.stop="callAttraction(attraction)">
                <text class="nav-icon">📞</text>
                <text class="nav-text">电话</text>
              </view>
            </view>
          </view>
        </view>

        <view class="load-more" v-if="hasMore && attractionsAll.length > 0">
          <text>{{ loadingMore ? '加载中...' : '加载更多' }}</text>
        </view>
        <view class="load-more" v-else-if="!hasMore && attractionsAll.length > 0">
          <text>已加载全部景点</text>
        </view>
      </scroll-view>
    </view>

    <!-- 底部安全区域 -->
    <view class="safe-area"></view>

    <!-- 定位权限提示弹窗 -->
    <view class="permission-modal" v-if="showPermissionModal">
      <view class="permission-content">
        <view class="permission-header">
          <text class="permission-title">位置权限申请</text>
        </view>
        <view class="permission-body">
          <text class="permission-text">为了提供精准的附近景点服务，需要获取您的位置信息</text>
        </view>
        <view class="permission-actions">
          <view class="permission-btn cancel" @tap="hidePermissionModal">取消</view>
          <view class="permission-btn confirm" @tap="requestLocationPermission">去设置</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
// 腾讯地图API配置
const TENCENT_MAP_KEY = '4DYBZ-7QXEC-CWM2S-AXAZR-YLVQF-C6BPY';
const TENCENT_MAP_BASE_URL = 'https://apis.map.qq.com';

export default {
  data() {
    return {
      searchKeyword: '',
      activeCategory: 'all',
      activeFilter: 'default',
      categories: [
        { id: 'all', name: '全部' },
        { id: 'historical', name: '历史古迹' },
        { id: 'park', name: '公园' },
        { id: 'museum', name: '博物馆' },
        { id: 'amusement', name: '游乐园' },
        { id: 'nature', name: '自然风光' },
        { id: 'culture', name: '文化体验' },
        { id: 'sightseeing', name: '观光' }
      ],
      filters: [
        { type: 'default', name: '距离优先' },
        { type: 'distance', name: '距离最近' }
      ],
      
      attractionsAll: [],
      currentPage: 1,
      pageSize: 20,
      hasMore: true,
      loading: false,
      loadingMore: false,
      refreshing: false,
      
      currentLocation: {
        latitude: null,
        longitude: null,
        city: ''
      },
      
      showPermissionModal: false,
      searchTimer: null
    }
  },
  computed: {
    filteredAttractions() {
      let attractions = [...this.attractionsAll];
      
      // 分类过滤（前端二次过滤）
      if (this.activeCategory !== 'all') {
        const category = this.categories.find(c => c.id === this.activeCategory);
        if (category && category.name !== '全部') {
          const categoryName = category.name;
          attractions = attractions.filter(attraction => {
            const name = attraction.name.toLowerCase();
            const categoryText = attraction.category.toLowerCase();
            return name.includes(categoryName.toLowerCase()) || categoryText.includes(categoryName.toLowerCase());
          });
        }
      }
      
      // 搜索关键词过滤
      if (this.searchKeyword && this.searchKeyword.trim()) {
        const keyword = this.searchKeyword.trim().toLowerCase();
        attractions = attractions.filter(attraction => 
          attraction.name.toLowerCase().includes(keyword) || 
          attraction.address.toLowerCase().includes(keyword)
        );
      }
      
      // 排序（按距离）
      if (this.activeFilter === 'distance' || this.activeFilter === 'default') {
        attractions.sort((a, b) => (a.distanceValue || 0) - (b.distanceValue || 0));
      }
      
      return attractions;
    }
  },
  onLoad() {
    this.getUserLocationAndLoadAttractions();
  },
  methods: {
    getUserLocationAndLoadAttractions() {
      this.loading = true;
      uni.getLocation({
        type: 'gcj02',
        success: (res) => {
          console.log('GPS定位成功:', res);
          this.currentLocation.latitude = res.latitude;
          this.currentLocation.longitude = res.longitude;
          this.resetAndLoad();
        },
        fail: (err) => {
          console.error('GPS定位失败:', err);
          if (err.errMsg && err.errMsg.includes('requiredPrivateInfos')) {
            uni.showModal({
              title: '定位配置缺失',
              content: '请在 app.json 中添加 "requiredPrivateInfos": ["getLocation"] 字段，并重新编译。',
              showCancel: false
            });
          }
          this.tryTencentIPLocation();
        }
      });
    },
    
    async tryTencentIPLocation() {
      try {
        const url = `${TENCENT_MAP_BASE_URL}/ws/location/v1/ip?key=${TENCENT_MAP_KEY}&output=json`;
        const response = await new Promise((resolve, reject) => {
          uni.request({
            url: url,
            method: 'GET',
            timeout: 10000,
            success: (res) => {
              if (res.statusCode === 200 && res.data.status === 0) {
                resolve(res.data);
              } else {
                reject(new Error(res.data.message || 'IP定位失败'));
              }
            },
            fail: reject
          });
        });
        if (response.status === 0 && response.result && response.result.location) {
          const location = response.result.location;
          this.currentLocation.latitude = location.lat;
          this.currentLocation.longitude = location.lng;
          uni.showToast({
            title: '使用IP定位',
            icon: 'none',
            duration: 1500
          });
          this.resetAndLoad();
        } else {
          throw new Error('IP定位无结果');
        }
      } catch (error) {
        console.error('IP定位失败:', error);
        this.loading = false;
        this.showPermissionModal = true;
      }
    },
    
    resetAndLoad() {
      this.attractionsAll = [];
      this.currentPage = 1;
      this.hasMore = true;
      this.loadAttractions(true);
    },
    
    async loadAttractions(reset = false) {
      if (!this.currentLocation.latitude || !this.currentLocation.longitude) {
        console.warn('位置未获取');
        return;
      }
      
      if (reset) {
        this.currentPage = 1;
        this.hasMore = true;
        this.loading = true;
        this.attractionsAll = [];
      } else {
        if (this.loadingMore || !this.hasMore) return;
        this.loadingMore = true;
      }
      
      // 构建搜索关键词
      let keyword = '景点';
      if (this.searchKeyword && this.searchKeyword.trim()) {
        keyword = this.searchKeyword.trim();
      } else if (this.activeCategory !== 'all') {
        const category = this.categories.find(c => c.id === this.activeCategory);
        if (category && category.name !== '全部') keyword = category.name + '景点';
      }
      
      const params = {
        key: TENCENT_MAP_KEY,
        boundary: `nearby(${this.currentLocation.latitude},${this.currentLocation.longitude},5000)`,
        keyword: keyword,
        page_size: this.pageSize,
        page_index: this.currentPage,
        order_by: '_distance'
      };
      
      try {
        const res = await this.requestAPI(`${TENCENT_MAP_BASE_URL}/ws/place/v1/search`, params);
        if (res.status === 0 && res.data && res.data.length) {
          const newAttractions = this.parseAttractionsFromAPI(res.data);
          if (reset) {
            this.attractionsAll = newAttractions;
          } else {
            this.attractionsAll = [...this.attractionsAll, ...newAttractions];
          }
          
          const total = res.count || 0;
          const loadedCount = this.currentPage * this.pageSize;
          this.hasMore = loadedCount < total && newAttractions.length === this.pageSize;
          if (this.hasMore) {
            this.currentPage++;
          }
        } else {
          if (this.currentPage === 1) {
            uni.showToast({
              title: '未找到附近景点',
              icon: 'none'
            });
          }
          this.hasMore = false;
        }
      } catch (error) {
        console.error('请求景点数据失败:', error);
        uni.showToast({
          title: '网络错误，请稍后重试',
          icon: 'none'
        });
      } finally {
        this.loading = false;
        this.loadingMore = false;
        this.refreshing = false;
      }
    },
    
    requestAPI(url, params) {
      return new Promise((resolve, reject) => {
        uni.request({
          url: url,
          method: 'GET',
          data: params,
          timeout: 15000,
          success: (res) => {
            if (res.statusCode === 200 && res.data.status === 0) {
              resolve(res.data);
            } else {
              reject(new Error(res.data.message || 'API请求失败'));
            }
          },
          fail: reject
        });
      });
    },
    
    parseAttractionsFromAPI(data) {
      return data.map((poi, index) => {
        // 提取分类标签
        let tags = [];
        if (poi.category) {
          const categoryParts = poi.category.split(',');
          tags = categoryParts.slice(0, 2);
        } else {
          tags = ['景点'];
        }
        
        // 提取营业时间
        let openingHours = '';
        if (poi.opening_hours) {
          openingHours = poi.opening_hours;
          if (openingHours.length > 30) {
            openingHours = openingHours.substring(0, 30) + '...';
          }
        }
        
        // 计算距离
        let distance = '';
        let distanceValue = 0;
        if (poi._distance) {
          distanceValue = poi._distance;
          if (poi._distance < 1000) {
            distance = `${Math.round(poi._distance)}m`;
          } else {
            distance = `${(poi._distance / 1000).toFixed(1)}km`;
          }
        } else {
          distance = '未知距离';
        }
        
        // 获取评分（腾讯地图部分POI有star_level字段，范围1-5）
        let rating = null;
        if (poi.star_level) {
          rating = (poi.star_level / 20).toFixed(1);
        } else {
          // 生成模拟评分（基于POI ID）
          const idHash = (poi.id || index.toString()).split('').reduce((a, b) => a + b.charCodeAt(0), 0);
          rating = (3.5 + (idHash % 15) / 10).toFixed(1);
        }
        
        return {
          id: poi.id || `temp_${Date.now()}_${index}`,
          name: poi.title || '景点',
          address: poi.address || poi.location?.address || '地址信息待补充',
          distance: distance,
          distanceValue: distanceValue,
          phone: poi.tel || '',
          latitude: poi.location?.lat || 0,
          longitude: poi.location?.lng || 0,
          category: poi.category || '',
          tags: tags,
          rating: rating,
          openingHours: openingHours || '营业时间请咨询',
          rawPoi: poi
        };
      });
    },
    
    onSearchInput() {
      if (this.searchTimer) clearTimeout(this.searchTimer);
      this.searchTimer = setTimeout(() => {
        this.activeCategory = 'all';
        this.resetAndLoad();
      }, 500);
    },
    
    onSearchConfirm() {
      this.activeCategory = 'all';
      this.resetAndLoad();
    },
    
    onSearchCancel() {
      this.searchKeyword = '';
      this.activeCategory = 'all';
      this.resetAndLoad();
    },
    
    onCategoryChange(categoryId) {
      this.activeCategory = categoryId;
      this.searchKeyword = '';
      this.resetAndLoad();
    },
    
    onFilterChange(filterType) {
      this.activeFilter = filterType;
      // computed 会自动重新排序
    },
    
    loadMore() {
      if (!this.hasMore || this.loadingMore || this.loading) return;
      this.loadAttractions(false);
    },
    
    onRefresh() {
      this.refreshing = true;
      this.resetAndLoad();
    },
    
    viewAttractionDetail(attraction) {
      let content = `地址：${attraction.address}\n`;
      content += `距离：${attraction.distance}\n`;
      if (attraction.openingHours) content += `营业时间：${attraction.openingHours}\n`;
      if (attraction.phone) content += `电话：${attraction.phone}\n`;
      if (attraction.rating) content += `评分：${attraction.rating}星\n`;
      
      uni.showModal({
        title: attraction.name,
        content: content,
        confirmText: '导航',
        cancelText: '关闭',
        success: (res) => {
          if (res.confirm) {
            this.navigateToAttraction(attraction);
          }
        }
      });
    },
    
    navigateToAttraction(attraction) {
      if (attraction.latitude && attraction.longitude) {
        uni.openLocation({
          latitude: parseFloat(attraction.latitude),
          longitude: parseFloat(attraction.longitude),
          name: attraction.name,
          address: attraction.address
        });
      } else {
        uni.showToast({
          title: '坐标信息缺失',
          icon: 'none'
        });
      }
    },
    
    callAttraction(attraction) {
      if (attraction.phone) {
        uni.makePhoneCall({
          phoneNumber: attraction.phone
        });
      } else {
        uni.showToast({
          title: '暂无联系电话',
          icon: 'none'
        });
      }
    },
    
    hidePermissionModal() {
      this.showPermissionModal = false;
    },
    
    requestLocationPermission() {
      this.hidePermissionModal();
      uni.openSetting({
        success: (res) => {
          if (res.authSetting['scope.userLocation']) {
            uni.showToast({
              title: '权限已开启，重新定位中',
              icon: 'success'
            });
            setTimeout(() => {
              this.getUserLocationAndLoadAttractions();
            }, 1000);
          }
        },
        fail: () => {
          uni.showToast({
            title: '打开设置失败',
            icon: 'none'
          });
        }
      });
    }
  }
}
</script>

<style scoped>
.ticket-page {
  height: 100vh;
  background: linear-gradient(135deg, #f0f6ff 0%, #e8ecff 100%);
  display: flex;
  flex-direction: column;
}

/* 顶部导航栏 */
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

/* 搜索栏 */
.search-section {
  padding: 30rpx;
  background-color: #fff;
  border-bottom: 1rpx solid #e0e8ff;
}

.search-box {
  background: linear-gradient(135deg, #f5f9ff 0%, #edf2ff 100%);
  border: 1rpx solid #d0deff;
  border-radius: 50rpx;
  box-shadow: 0 4rpx 12rpx rgba(184, 212, 255, 0.2);
}

.search-input {
  display: flex;
  align-items: center;
  padding: 20rpx 30rpx;
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

.search-cancel {
  margin-left: 20rpx;
}

.search-cancel text {
  font-size: 28rpx;
  color: #5a7bdb;
}

/* 分类导航（文字胶囊） */
.category-section {
  background: #fff;
  padding: 20rpx 30rpx;
  border-bottom: 1rpx solid #e0e8ff;
}

.category-scroll {
  white-space: nowrap;
}

.category-item {
  display: inline-flex;
  align-items: center;
  padding: 0 10rpx;
  transition: all 0.3s ease;
}

.category-name {
  font-size: 26rpx;
  color: #8a9bc1;
  transition: all 0.3s ease;
  padding: 12rpx 24rpx;
  border-radius: 40rpx;
  background: transparent;
}

.category-item.active .category-name {
  color: #5a7bdb;
  font-weight: 600;
  background: linear-gradient(135deg, #f0f7ff, #e8ecff);
  box-shadow: 0 2rpx 8rpx rgba(90, 123, 219, 0.15);
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

/* 景点列表 */
.attraction-list {
  flex: 1;
  overflow: hidden;
}

.list-scroll {
  height: 100%;
  padding: 20rpx 0; /* 移除左右内边距，让卡片自身通过 margin 居中 */
}

/* 卡片样式（居中优化） */
.attraction-card {
  width: 90%;                /* 宽度占屏幕的90% */
  margin: 0 auto 30rpx auto; /* 水平居中，底部间距 */
  background: linear-gradient(135deg, #ffffff 0%, #f8fbff 100%);
  border-radius: 24rpx;
  overflow: hidden;
  box-shadow: 0 6rpx 20rpx rgba(184, 212, 255, 0.3);
  border: 1rpx solid #e0e8ff;
  transition: all 0.3s ease;
}

.attraction-card:active {
  transform: translateY(4rpx);
  box-shadow: 0 2rpx 10rpx rgba(184, 212, 255, 0.2);
}

.attraction-info-full {
  padding: 30rpx;
}

.attraction-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.attraction-name {
  font-size: 34rpx;
  font-weight: 700;
  color: #3a5bc7;
  text-shadow: 0 2rpx 4rpx rgba(184, 212, 255, 0.3);
  flex: 1;
  margin-right: 20rpx;
}

.rating-tag {
  background: rgba(255, 255, 255, 0.9);
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
  font-size: 24rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
  background: linear-gradient(135deg, #fff8e7, #fff0d0);
}

.rating-star {
  font-size: 26rpx;
  margin-right: 4rpx;
  color: #ff9500;
}

.rating-score {
  color: #ff9500;
}

.attraction-desc {
  font-size: 28rpx;
  color: #666;
  line-height: 1.5;
  margin-bottom: 20rpx;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}

.attraction-tags {
  display: flex;
  flex-wrap: wrap;
  margin-bottom: 20rpx;
}

.tag {
  background: linear-gradient(135deg, #b8d4ff, #bcc4e8);
  color: #3a5bc7;
  padding: 10rpx 20rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
  margin-right: 15rpx;
  margin-bottom: 10rpx;
  font-weight: 500;
  box-shadow: 0 2rpx 6rpx rgba(184, 212, 255, 0.4);
}

.attraction-location {
  display: flex;
  align-items: center;
  margin-bottom: 15rpx;
}

.location-icon {
  width: 28rpx;
  height: 28rpx;
  margin-right: 10rpx;
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

.attraction-info-row {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.info-icon {
  font-size: 24rpx;
  margin-right: 10rpx;
}

.info-text {
  font-size: 24rpx;
  color: #5a7bdb;
  background: #f0f7ff;
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
}

/* 操作按钮 */
.attraction-actions {
  display: flex;
  gap: 20rpx;
  margin-top: 10rpx;
}

.nav-button {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16rpx 20rpx;
  border-radius: 40rpx;
  transition: all 0.3s ease;
  box-shadow: 0 4rpx 12rpx rgba(90, 123, 219, 0.3);
}

.nav-button:active {
  transform: translateY(2rpx);
  opacity: 0.9;
}

.nav-button.navigation {
  background: linear-gradient(135deg, #5a7bdb, #6c8fef);
}

.nav-button.call {
  background: linear-gradient(135deg, #6bcf7f, #5bbd6f);
}

.nav-icon {
  font-size: 28rpx;
  margin-right: 10rpx;
}

.nav-text {
  font-size: 28rpx;
  color: #fff;
  font-weight: 600;
}

.load-more {
  text-align: center;
  padding: 30rpx;
  color: #8a9bc1;
  font-size: 26rpx;
}

.safe-area {
  height: env(safe-area-inset-bottom);
  background: transparent;
}

.loading-container, .empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx 0;
}

.loading-text, .empty-text {
  font-size: 28rpx;
  color: #8a9bc1;
}

.empty-sub {
  font-size: 24rpx;
  color: #b0c0e0;
  margin-top: 10rpx;
}

/* 权限弹窗 */
.permission-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.permission-content {
  background: #fff;
  border-radius: 20rpx;
  width: 600rpx;
  overflow: hidden;
}

.permission-header {
  padding: 40rpx 30rpx 20rpx;
  text-align: center;
}

.permission-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
}

.permission-body {
  padding: 0 30rpx 40rpx;
  text-align: center;
}

.permission-text {
  font-size: 28rpx;
  color: #666;
  line-height: 1.5;
}

.permission-actions {
  display: flex;
  border-top: 1rpx solid #eee;
}

.permission-btn {
  flex: 1;
  text-align: center;
  padding: 30rpx;
  font-size: 28rpx;
  transition: all 0.3s ease;
}

.permission-btn.cancel {
  color: #999;
  border-right: 1rpx solid #eee;
}

.permission-btn.confirm {
  color: #5a7bdb;
  font-weight: 500;
}

.permission-btn:active {
  background: #f5f5f5;
}

/* 卡片入场动画 */
.attraction-card {
  animation: fadeIn 0.5s ease forwards;
}

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
</style>