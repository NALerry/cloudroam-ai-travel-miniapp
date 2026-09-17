<template>
  <view class="food-page">
    <!-- 顶部导航栏 -->
    <view class="nav-bar">
      <view 
        class="nav-item" 
        :class="{ active: currentTab === 'restaurant' }"
        @tap="switchTab('restaurant')"
      >
        <text class="nav-text">餐厅</text>
      </view>
      <view 
        class="nav-item" 
        :class="{ active: currentTab === 'snack' }"
        @tap="switchTab('snack')"
      >
        <text class="nav-text">小吃街</text>
      </view>
    </view>

    <!-- 内容区域 -->
    <view class="content-section">
      <!-- 餐厅内容 -->
      <view class="tab-content" v-if="currentTab === 'restaurant'">
        <scroll-view class="content-scroll" scroll-y @scrolltolower="loadMoreRestaurants" :refresher-enabled="true" :refresher-triggered="refreshingRestaurant" @refresherrefresh="onRefreshRestaurant">
          <!-- 搜索区域 -->
          <view class="search-box">
            <view class="search-input">
              <image class="search-icon" src="/static/icons/general/search1.png"></image>
              <input 
                type="text" 
                placeholder="搜索餐厅名称或菜系" 
                v-model="restaurantKeyword"
                @confirm="searchRestaurant"
              />
            </view>
          </view>
          
          <!-- 分类导航（简化版：基于API返回的分类动态生成） -->
          <view class="category-section" v-if="restaurantCategories.length > 0">
            <scroll-view class="category-scroll" scroll-x :show-scrollbar="false">
              <view 
                class="category-item" 
                v-for="category in restaurantCategories" 
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
          
          <!-- 餐厅列表 -->
          <view class="restaurant-list">
            <view v-if="restaurantLoading && restaurantList.length === 0" class="loading-container">
              <text class="loading-text">正在获取附近餐厅...</text>
            </view>
            <view v-else-if="filteredRestaurants.length === 0 && !restaurantLoading" class="empty-container">
              <text class="empty-text">没有找到餐厅</text>
              <text class="empty-sub">尝试切换筛选条件或搜索关键词</text>
            </view>
            <view 
              class="restaurant-card" 
              v-for="item in filteredRestaurants" 
              :key="item.id"
              @tap="viewRestaurantDetail(item)"
            >
              <view class="restaurant-info-full">
                <view class="restaurant-header">
                  <text class="restaurant-name">{{ item.name }}</text>
                  <view class="rating-tag">
                    <text class="rating-star">★</text>
                    <text class="rating-score">{{ item.rating }}</text>
                  </view>
                </view>
                <text class="restaurant-desc">{{ item.description }}</text>
                <view class="restaurant-tags">
                  <text 
                    class="tag" 
                    v-for="(tag, index) in item.tags" 
                    :key="index"
                  >{{ tag }}</text>
                </view>
                <view class="restaurant-location">
                  <image class="location-icon" src="/static/icons/general/location.png"></image>
                  <text class="location-text">{{ item.address }}</text>
                  <text class="distance">{{ item.distance }}</text>
                </view>
                <view class="restaurant-contact" v-if="item.phone">
                  <text class="contact-text">📞 {{ item.phone }}</text>
                </view>
                <view class="restaurant-promo" v-if="item.openingHours">
                  <text>{{ item.openingHours }}</text>
                </view>
                <!-- 导航按钮 -->
                <view class="nav-button" @tap.stop="goNavigation(item)">
                  <text class="nav-icon">🗺️</text>
                  <text class="nav-text">导航</text>
                </view>
              </view>
            </view>
            <view class="load-more" v-if="restaurantHasMore && restaurantList.length > 0">
              <text>{{ restaurantLoadingMore ? '加载中...' : '加载更多' }}</text>
            </view>
            <view class="load-more" v-else-if="!restaurantHasMore && restaurantList.length > 0">
              <text>已加载全部餐厅</text>
            </view>
          </view>
        </scroll-view>
      </view>

      <!-- 小吃街内容 -->
      <view class="tab-content" v-if="currentTab === 'snack'">
        <scroll-view class="content-scroll" scroll-y @scrolltolower="loadMoreSnacks" :refresher-enabled="true" :refresher-triggered="refreshingSnack" @refresherrefresh="onRefreshSnack">
          <!-- 搜索区域 -->
          <view class="search-box">
            <view class="search-input">
              <image class="search-icon" src="/static/icons/general/search1.png"></image>
              <input 
                type="text" 
                placeholder="搜索小吃名称或地点" 
                v-model="snackKeyword"
                @confirm="searchSnack"
              />
            </view>
          </view>

          <!-- 小吃街筛选条件 -->
          <view class="filter-section">
            <view class="filter-row">
              <view 
                class="filter-item" 
                v-for="filter in snackFilters" 
                :key="filter.type"
                :class="{ active: activeSnackFilter === filter.type }"
                @tap="onSnackFilterChange(filter.type)"
              >
                <text>{{ filter.name }}</text>
                <image class="filter-arrow" src="/static/icons/general/arrow-down.png" mode="aspectFit"></image>
              </view>
            </view>
          </view>
          
          <!-- 小吃街列表 -->
          <view class="snack-list">
            <view v-if="snackLoading && snackList.length === 0" class="loading-container">
              <text class="loading-text">正在获取附近小吃街...</text>
            </view>
            <view v-else-if="filteredSnacks.length === 0 && !snackLoading" class="empty-container">
              <text class="empty-text">没有找到小吃街</text>
              <text class="empty-sub">尝试切换筛选条件或搜索关键词</text>
            </view>
            <view 
              class="snack-card" 
              v-for="item in filteredSnacks" 
              :key="item.id"
              @tap="viewSnackDetail(item)"
            >
              <view class="snack-info-full">
                <view class="snack-header">
                  <text class="snack-name">{{ item.name }}</text>
                  <view class="rating-tag">
                    <text class="rating-star">★</text>
                    <text class="rating-score">{{ item.rating }}</text>
                  </view>
                </view>
                <text class="snack-desc">{{ item.description }}</text>
                <view class="snack-tags">
                  <text 
                    class="tag" 
                    v-for="(tag, index) in item.tags" 
                    :key="index"
                  >{{ tag }}</text>
                </view>
                <view class="snack-location">
                  <image class="location-icon" src="/static/icons/general/location.png"></image>
                  <text class="location-text">{{ item.address }}</text>
                  <text class="distance">{{ item.distance }}</text>
                </view>
                <view class="snack-contact" v-if="item.phone">
                  <text class="contact-text">📞 {{ item.phone }}</text>
                </view>
                <view class="snack-tips" v-if="item.openingHours">
                  <text class="tip-item">{{ item.openingHours }}</text>
                </view>
                <!-- 导航按钮 -->
                <view class="nav-button" @tap.stop="goNavigation(item)">
                  <text class="nav-icon">🗺️</text>
                  <text class="nav-text">导航</text>
                </view>
              </view>
            </view>
            <view class="load-more" v-if="snackHasMore && snackList.length > 0">
              <text>{{ snackLoadingMore ? '加载中...' : '加载更多' }}</text>
            </view>
            <view class="load-more" v-else-if="!snackHasMore && snackList.length > 0">
              <text>已加载全部小吃街</text>
            </view>
          </view>
        </scroll-view>
      </view>
    </view>

    <!-- 定位权限提示弹窗 -->
    <view class="permission-modal" v-if="showPermissionModal">
      <view class="permission-content">
        <view class="permission-header">
          <text class="permission-title">位置权限申请</text>
        </view>
        <view class="permission-body">
          <text class="permission-text">为了提供精准的附近美食服务，需要获取您的位置信息</text>
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
      currentTab: 'restaurant',
      
      // 餐厅相关数据
      restaurantKeyword: '',
      restaurantList: [],
      restaurantPage: 1,
      restaurantPageSize: 20,
      restaurantHasMore: true,
      restaurantLoading: false,
      restaurantLoadingMore: false,
      refreshingRestaurant: false,
      restaurantCategories: [{ id: 'all', name: '全部' }],
      
      // 小吃街相关数据
      snackKeyword: '',
      snackList: [],
      snackPage: 1,
      snackPageSize: 20,
      snackHasMore: true,
      snackLoading: false,
      snackLoadingMore: false,
      refreshingSnack: false,
      
      // 筛选条件
      activeCategory: 'all',
      activeFilter: 'all',
      activeSnackFilter: 'all',
      
      filters: [
        { type: 'all', name: '智能排序' },
        { type: 'distance', name: '距离最近' },
        { type: 'rating', name: '评分最高' }
      ],
      snackFilters: [
        { type: 'all', name: '智能排序' },
        { type: 'distance', name: '距离最近' },
        { type: 'rating', name: '评分最高' }
      ],
      
      // 定位信息
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
    filteredRestaurants() {
      let restaurants = [...this.restaurantList];
      
      // 分类过滤
      if (this.activeCategory !== 'all') {
        const categoryName = this.getCategoryNameById(this.activeCategory);
        restaurants = restaurants.filter(item => 
          item.category && item.category.includes(categoryName)
        );
      }
      
      // 排序
      switch (this.activeFilter) {
        case 'distance':
          restaurants.sort((a, b) => (a.distanceValue || 0) - (b.distanceValue || 0));
          break;
        case 'rating':
          restaurants.sort((a, b) => b.ratingValue - a.ratingValue);
          break;
      }
      
      return restaurants;
    },
    
    filteredSnacks() {
      let snacks = [...this.snackList];
      
      switch (this.activeSnackFilter) {
        case 'distance':
          snacks.sort((a, b) => (a.distanceValue || 0) - (b.distanceValue || 0));
          break;
        case 'rating':
          snacks.sort((a, b) => b.ratingValue - a.ratingValue);
          break;
      }
      
      return snacks;
    }
  },
  
  onLoad() {
    this.getUserLocationAndLoadData();
  },
  
  methods: {
    // 获取用户位置
    getUserLocationAndLoadData() {
      uni.getLocation({
        type: 'gcj02',
        success: (res) => {
          console.log('定位成功:', res);
          this.currentLocation.latitude = res.latitude;
          this.currentLocation.longitude = res.longitude;
          this.loadCurrentTabData(true);
        },
        fail: (err) => {
          console.error('定位失败:', err);
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
          uni.showToast({ title: '使用IP定位', icon: 'none', duration: 1500 });
          this.loadCurrentTabData(true);
        } else {
          throw new Error('IP定位无结果');
        }
      } catch (error) {
        console.error('IP定位失败:', error);
        this.showPermissionModal = true;
      }
    },
    
    // 加载当前标签页数据
    loadCurrentTabData(reset = false) {
      if (this.currentTab === 'restaurant') {
        this.loadRestaurants(reset);
      } else {
        this.loadSnacks(reset);
      }
    },
    
    // 加载餐厅数据
    async loadRestaurants(reset = false) {
      if (!this.currentLocation.latitude || !this.currentLocation.longitude) {
        console.warn('位置未获取');
        return;
      }
      
      if (reset) {
        this.restaurantPage = 1;
        this.restaurantHasMore = true;
        this.restaurantLoading = true;
        this.restaurantList = [];
      } else {
        if (this.restaurantLoadingMore || !this.restaurantHasMore) return;
        this.restaurantLoadingMore = true;
      }
      
      const keyword = this.restaurantKeyword.trim() || '餐厅';
      const params = {
        key: TENCENT_MAP_KEY,
        boundary: `nearby(${this.currentLocation.latitude},${this.currentLocation.longitude},3000)`,
        keyword: keyword,
        page_size: this.restaurantPageSize,
        page_index: this.restaurantPage,
        order_by: '_distance'
      };
      
      try {
        const res = await this.requestAPI(`${TENCENT_MAP_BASE_URL}/ws/place/v1/search`, params);
        if (res.status === 0 && res.data && res.data.length) {
          const newRestaurants = this.parseFoodFromAPI(res.data);
          if (reset) {
            this.restaurantList = newRestaurants;
          } else {
            this.restaurantList = [...this.restaurantList, ...newRestaurants];
          }
          this.updateRestaurantCategories();
          
          const total = res.count || 0;
          const loadedCount = this.restaurantPage * this.restaurantPageSize;
          this.restaurantHasMore = loadedCount < total && newRestaurants.length === this.restaurantPageSize;
          if (this.restaurantHasMore) {
            this.restaurantPage++;
          }
        } else {
          if (this.restaurantPage === 1) {
            uni.showToast({ title: '未找到附近餐厅', icon: 'none' });
          }
          this.restaurantHasMore = false;
        }
      } catch (error) {
        console.error('请求餐厅数据失败:', error);
        uni.showToast({ title: '网络错误，请稍后重试', icon: 'none' });
      } finally {
        this.restaurantLoading = false;
        this.restaurantLoadingMore = false;
        this.refreshingRestaurant = false;
      }
    },
    
    // 加载小吃街数据
    async loadSnacks(reset = false) {
      if (!this.currentLocation.latitude || !this.currentLocation.longitude) {
        console.warn('位置未获取');
        return;
      }
      
      if (reset) {
        this.snackPage = 1;
        this.snackHasMore = true;
        this.snackLoading = true;
        this.snackList = [];
      } else {
        if (this.snackLoadingMore || !this.snackHasMore) return;
        this.snackLoadingMore = true;
      }
      
      const keyword = this.snackKeyword.trim() || '小吃街';
      const params = {
        key: TENCENT_MAP_KEY,
        boundary: `nearby(${this.currentLocation.latitude},${this.currentLocation.longitude},3000)`,
        keyword: keyword,
        page_size: this.snackPageSize,
        page_index: this.snackPage,
        order_by: '_distance'
      };
      
      try {
        const res = await this.requestAPI(`${TENCENT_MAP_BASE_URL}/ws/place/v1/search`, params);
        if (res.status === 0 && res.data && res.data.length) {
          const newSnacks = this.parseFoodFromAPI(res.data);
          if (reset) {
            this.snackList = newSnacks;
          } else {
            this.snackList = [...this.snackList, ...newSnacks];
          }
          
          const total = res.count || 0;
          const loadedCount = this.snackPage * this.snackPageSize;
          this.snackHasMore = loadedCount < total && newSnacks.length === this.snackPageSize;
          if (this.snackHasMore) {
            this.snackPage++;
          }
        } else {
          if (this.snackPage === 1) {
            uni.showToast({ title: '未找到附近小吃街', icon: 'none' });
          }
          this.snackHasMore = false;
        }
      } catch (error) {
        console.error('请求小吃街数据失败:', error);
        uni.showToast({ title: '网络错误，请稍后重试', icon: 'none' });
      } finally {
        this.snackLoading = false;
        this.snackLoadingMore = false;
        this.refreshingSnack = false;
      }
    },
    
    // 解析API返回的美食数据
    parseFoodFromAPI(data) {
      return data.map((poi, index) => {
        // 提取分类信息
        let category = '美食';
        let tags = [];
        if (poi.category) {
          const categoryParts = poi.category.split(':');
          category = categoryParts[categoryParts.length - 1] || '美食';
          tags = [category];
        }
        
        // 从标题提取额外标签
        const title = poi.title || '';
        if (title.includes('火锅')) tags.push('火锅');
        if (title.includes('烧烤')) tags.push('烧烤');
        if (title.includes('川菜')) tags.push('川菜');
        if (title.includes('粤菜')) tags.push('粤菜');
        if (title.includes('日料')) tags.push('日料');
        if (title.includes('西餐')) tags.push('西餐');
        
        // 生成模拟评分（基于POI ID的确定性随机，范围3.5-5.0）
        const idHash = (poi.id || index.toString()).split('').reduce((a, b) => a + b.charCodeAt(0), 0);
        const ratingValue = 3.5 + (idHash % 15) / 10;
        const rating = ratingValue.toFixed(1);
        
        // 距离处理
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
        
        // 描述信息
        let description = poi.address || '';
        if (description.length > 50) description = description.substring(0, 50) + '...';
        
        // 营业时间
        let openingHours = '';
        if (poi.opening_hours) {
          openingHours = poi.opening_hours.length > 30 ? poi.opening_hours.substring(0, 30) + '...' : poi.opening_hours;
        }
        
        return {
          id: poi.id || `temp_${Date.now()}_${index}`,
          name: poi.title || '美食店铺',
          address: poi.address || poi.location?.address || '地址信息待补充',
          distance: distance,
          distanceValue: distanceValue,
          phone: poi.tel || '',
          latitude: poi.location?.lat || 0,
          longitude: poi.location?.lng || 0,
          rating: rating,
          ratingValue: ratingValue,
          category: category,
          tags: tags.slice(0, 3),
          description: description,
          openingHours: openingHours,
          rawPoi: poi
        };
      });
    },
    
    // 更新餐厅分类列表
    updateRestaurantCategories() {
      const categoriesSet = new Set(['all']);
      this.restaurantList.forEach(item => {
        if (item.category) categoriesSet.add(item.category);
      });
      
      const newCategories = Array.from(categoriesSet).map(cat => ({
        id: cat === 'all' ? 'all' : cat,
        name: cat === 'all' ? '全部' : cat
      }));
      
      this.restaurantCategories = newCategories;
      
      // 如果当前选中的分类不在新列表中，重置为全部
      if (!this.restaurantCategories.find(c => c.id === this.activeCategory)) {
        this.activeCategory = 'all';
      }
    },
    
    getCategoryNameById(categoryId) {
      const category = this.restaurantCategories.find(c => c.id === categoryId);
      return category ? category.name : '';
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
    
    // 切换标签
    switchTab(tab) {
      if (this.currentTab === tab) return;
      this.currentTab = tab;
      this.loadCurrentTabData(true);
    },
    
    // 搜索餐厅
    searchRestaurant() {
      if (this.searchTimer) clearTimeout(this.searchTimer);
      this.searchTimer = setTimeout(() => {
        this.loadRestaurants(true);
      }, 300);
    },
    
    // 搜索小吃
    searchSnack() {
      if (this.searchTimer) clearTimeout(this.searchTimer);
      this.searchTimer = setTimeout(() => {
        this.loadSnacks(true);
      }, 300);
    },
    
    onCategoryChange(categoryId) {
      this.activeCategory = categoryId;
    },
    
    onFilterChange(filterType) {
      this.activeFilter = filterType;
    },
    
    onSnackFilterChange(filterType) {
      this.activeSnackFilter = filterType;
    },
    
    loadMoreRestaurants() {
      if (!this.restaurantHasMore || this.restaurantLoadingMore || this.restaurantLoading) return;
      this.loadRestaurants(false);
    },
    
    loadMoreSnacks() {
      if (!this.snackHasMore || this.snackLoadingMore || this.snackLoading) return;
      this.loadSnacks(false);
    },
    
    onRefreshRestaurant() {
      this.refreshingRestaurant = true;
      this.loadRestaurants(true);
    },
    
    onRefreshSnack() {
      this.refreshingSnack = true;
      this.loadSnacks(true);
    },
    
    viewRestaurantDetail(item) {
      uni.navigateTo({
        url: `/pages/food/restaurant-detail?id=${item.id}&name=${encodeURIComponent(item.name)}&lat=${item.latitude}&lng=${item.longitude}`
      });
    },
    
    viewSnackDetail(item) {
      uni.navigateTo({
        url: `/pages/food/snack-detail?id=${item.id}&name=${encodeURIComponent(item.name)}&lat=${item.latitude}&lng=${item.longitude}`
      });
    },
    
    // 导航功能
    goNavigation(item) {
      // 校验坐标有效性
      if (!item.latitude || !item.longitude || item.latitude === 0 || item.longitude === 0) {
        uni.showToast({
          title: '该地点缺少有效坐标，无法导航',
          icon: 'none',
          duration: 2000
        });
        return;
      }
      
      // 调用地图导航
      uni.openLocation({
        latitude: parseFloat(item.latitude),
        longitude: parseFloat(item.longitude),
        name: item.name,
        address: item.address,
        success: () => {
          console.log('打开地图成功');
        },
        fail: (err) => {
          console.error('打开地图失败:', err);
          uni.showToast({
            title: '打开地图失败，请稍后重试',
            icon: 'none',
            duration: 2000
          });
        }
      });
    },
    
    hidePermissionModal() {
      this.showPermissionModal = false;
    },
    
    requestLocationPermission() {
      this.hidePermissionModal();
      uni.openSetting({
        success: (res) => {
          if (res.authSetting['scope.userLocation']) {
            uni.showToast({ title: '权限已开启，重新定位中', icon: 'success' });
            setTimeout(() => {
              this.getUserLocationAndLoadData();
            }, 1000);
          }
        },
        fail: () => {
          uni.showToast({ title: '打开设置失败', icon: 'none' });
        }
      });
    }
  }
}
</script>

<style scoped>
.food-page {
  height: 100vh;
  background: linear-gradient(135deg, #f0f6ff 0%, #e8ecff 100%);
  display: flex;
  flex-direction: column;
}

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

.category-item.active .category-name {
  color: #5a7bdb;
  font-weight: 600;
  background: linear-gradient(135deg, #b8d4ff, #bcc4e8);
  padding: 10rpx 20rpx;
  border-radius: 25rpx;
}

.category-name {
  font-size: 26rpx;
  color: #8a9bc1;
  transition: all 0.3s ease;
  padding: 10rpx 20rpx;
  border-radius: 25rpx;
}

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

.restaurant-list, .snack-list {
  padding: 0 30rpx 30rpx;
}

.restaurant-card, .snack-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fbff 100%);
  border-radius: 24rpx;
  overflow: hidden;
  margin-top: 30rpx;
  box-shadow: 0 6rpx 20rpx rgba(184, 212, 255, 0.3);
  border: 1rpx solid #e0e8ff;
  transition: all 0.3s ease;
}

.restaurant-card:active, .snack-card:active {
  transform: translateY(4rpx);
  box-shadow: 0 2rpx 10rpx rgba(184, 212, 255, 0.2);
}

.restaurant-info-full, .snack-info-full {
  padding: 30rpx;
}

.restaurant-header, .snack-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.restaurant-name, .snack-name {
  font-size: 34rpx;
  font-weight: 700;
  color: #3a5bc7;
  text-shadow: 0 2rpx 4rpx rgba(184, 212, 255, 0.3);
  flex: 1;
  margin-right: 20rpx;
}

.rating-tag {
  background: rgba(255, 255, 255, 0.9);
  color: #ff9500;
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

.restaurant-desc, .snack-desc {
  font-size: 28rpx;
  color: #666;
  line-height: 1.5;
  margin-bottom: 20rpx;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}

.restaurant-tags, .snack-tags {
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

.restaurant-location, .snack-location {
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

.restaurant-contact, .snack-contact {
  margin-bottom: 12rpx;
}

.contact-text {
  font-size: 24rpx;
  color: #666;
}

.restaurant-promo, .snack-tips {
  margin-top: 12rpx;
}

.tip-item {
  background: linear-gradient(135deg, #fff3e0, #ffecb3);
  color: #ff9800;
  padding: 10rpx 20rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
  display: inline-block;
  border: 1rpx solid #ffe0b2;
  font-weight: 500;
  box-shadow: 0 2rpx 6rpx rgba(255, 167, 38, 0.2);
}

/* 导航按钮样式 */
.nav-button {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #5a7bdb, #6c8fef);
  margin-top: 20rpx;
  padding: 16rpx 20rpx;
  border-radius: 40rpx;
  transition: all 0.3s ease;
  box-shadow: 0 4rpx 12rpx rgba(90, 123, 219, 0.3);
}

.nav-button:active {
  transform: translateY(2rpx);
  opacity: 0.9;
}

.nav-icon {
  font-size: 28rpx;
  margin-right: 10rpx;
}

.nav-button .nav-text {
  font-size: 28rpx;
  color: #fff;
  font-weight: 600;
}

.load-more {
  text-align: center;
  padding: 30rpx;
  color: #b8d4ff;
  font-size: 26rpx;
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
  color: #999;
}

.empty-sub {
  font-size: 24rpx;
  color: #ccc;
  margin-top: 10rpx;
}

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
  color: #b8d4ff;
  font-weight: 500;
}

.permission-btn:active {
  background: #f5f5f5;
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

.restaurant-card, .snack-card {
  animation: fadeIn 0.5s ease forwards;
}
</style>