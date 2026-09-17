<template>
  <view class="shopping-page">
    <!-- 顶部导航栏 -->
    <view class="nav-bar">
      <view 
        class="nav-item" 
        :class="{ active: currentTab === 'online' }"
        @tap="switchTab('online')"
      >
        <text class="nav-text">附近商场</text>
      </view>
      <view 
        class="nav-item" 
        :class="{ active: currentTab === 'offline' }"
        @tap="switchTab('offline')"
      >
        <text class="nav-text">特色街区</text>
      </view>
    </view>

    <!-- 内容区域 -->
    <view class="content-section">
      <!-- 线上购物内容（附近商场/购物中心） -->
      <view class="tab-content" v-if="currentTab === 'online'">
        <scroll-view class="content-scroll" scroll-y>
          <!-- 搜索区域 -->
          <view class="search-box">
            <view class="search-input">
              <image class="search-icon" src="/static/icons/general/search1.png"></image>
              <input 
                type="text" 
                placeholder="搜索商场或品牌" 
                v-model="onlineKeyword"
                @confirm="searchOnline"
              />
            </view>
          </view>
          
          <!-- 分类导航（保留图标筛选） -->
          <view class="category-section">
            <scroll-view class="category-scroll" scroll-x :show-scrollbar="false">
              <view 
                class="category-item" 
                v-for="category in onlineCategories" 
                :key="category.id"
                :class="{ active: activeOnlineCategory === category.id }"
                @tap="onOnlineCategoryChange(category.id)"
              >
                <image class="category-icon" :src="category.icon" mode="aspectFit"></image>
                <text class="category-name">{{ category.name }}</text>
              </view>
            </scroll-view>
          </view>

          <!-- 筛选条件（排序） -->
          <view class="filter-section">
            <view class="filter-row">
              <view 
                class="filter-item" 
                v-for="filter in onlineFilters" 
                :key="filter.type"
                :class="{ active: activeOnlineFilter === filter.type }"
                @tap="onOnlineFilterChange(filter.type)"
              >
                <text>{{ filter.name }}</text>
                <image class="filter-arrow" src="/static/icons/general/arrow-down.png" mode="aspectFit"></image>
              </view>
            </view>
          </view>
          
          <!-- 线上购物场所列表（真实API数据） -->
          <view class="shopping-list" v-if="!onlineLoading || onlineList.length">
            <view 
              class="shopping-card" 
              v-for="item in sortedOnlineList" 
              :key="item.id"
              @tap="viewPlaceDetail(item)"
            >
              <view class="card-header">
                <text class="place-name">{{ item.name }}</text>
                <view class="place-tags">
                  <text class="tag" v-if="item.is24h">24小时</text>
                  <text class="tag discount-tag" v-if="item.hasDiscount">优惠活动</text>
                  <text class="tag brand-tag">{{ item.categoryName || '商场' }}</text>
                </view>
              </view>
              
              <view class="place-info">
                <view class="info-row">
                  <image class="info-icon" src="/static/icons/general/location.png" mode="aspectFit"></image>
                  <text class="info-text">{{ item.address }}</text>
                </view>
                <view class="info-row">
                  <image class="info-icon" src="/static/icons/general/distance.png" mode="aspectFit"></image>
                  <text class="info-text">{{ item.distance }}</text>
                </view>
              </view>

              <view class="detail-section" v-if="item.openingHours || item.phone">
                <view class="detail-item" v-if="item.openingHours">
                  <text class="detail-label">营业时间</text>
                  <text class="detail-value">{{ item.openingHours }}</text>
                </view>
                <view class="detail-item" v-if="item.phone">
                  <text class="detail-label">联系电话</text>
                  <text class="detail-value">{{ item.phone }}</text>
                </view>
              </view>

              <view class="card-actions">
                <view class="action-btn nav" @tap.stop="navigateToPlace(item)">
                  <image class="action-icon" src="/static/icons/general/navigation.png" mode="aspectFit"></image>
                  <text>导航</text>
                </view>
                <view class="action-btn call" @tap.stop="callPlace(item)">
                  <image class="action-icon" src="/static/icons/general/call.png" mode="aspectFit"></image>
                  <text>电话</text>
                </view>
                <view class="action-btn fav" @tap.stop="toggleFavorite(item)">
                  <image 
                    class="action-icon" 
                    :src="item.isFavorite ? '/static/icons/general/heart-filled.png' : '/static/icons/general/heart.png'" 
                    mode="aspectFit"
                  ></image>
                  <text>收藏</text>
                </view>
              </view>
            </view>
          </view>

          <!-- 加载状态 -->
          <view v-if="onlineLoading && onlineList.length === 0" class="loading-container">
            <text class="loading-text">正在搜索附近商场...</text>
          </view>
          <view v-else-if="!onlineLoading && onlineList.length === 0" class="empty-container">
            <image class="empty-icon" src="/static/icons/general/empty.png" mode="aspectFit"></image>
            <text class="empty-text">未找到相关场所</text>
            <text class="empty-sub">尝试切换分类或搜索关键词</text>
          </view>

          <view class="load-more" v-if="onlineHasMore && onlineList.length > 0">
            <text>{{ onlineLoadingMore ? '加载中...' : '上拉加载更多' }}</text>
          </view>
          <view class="load-more" v-else-if="!onlineHasMore && onlineList.length > 0">
            <text>已加载全部场所</text>
          </view>
        </scroll-view>
      </view>

      <!-- 线下购物内容（特色街区/步行街） -->
      <view class="tab-content" v-if="currentTab === 'offline'">
        <scroll-view class="content-scroll" scroll-y>
          <!-- 搜索区域 -->
          <view class="search-box">
            <view class="search-input">
              <image class="search-icon" src="/static/icons/general/search1.png"></image>
              <input 
                type="text" 
                placeholder="搜索步行街或特色街区" 
                v-model="offlineKeyword"
                @confirm="searchOffline"
              />
            </view>
          </view>

          <!-- 线下购物筛选条件 -->
          <view class="filter-section">
            <view class="filter-row">
              <view 
                class="filter-item" 
                v-for="filter in offlineFilters" 
                :key="filter.type"
                :class="{ active: activeOfflineFilter === filter.type }"
                @tap="onOfflineFilterChange(filter.type)"
              >
                <text>{{ filter.name }}</text>
                <image class="filter-arrow" src="/static/icons/general/arrow-down.png" mode="aspectFit"></image>
              </view>
            </view>
          </view>
          
          <!-- 线下购物地点列表（真实API数据） -->
          <view class="shopping-list" v-if="!offlineLoading || offlineList.length">
            <view 
              class="shopping-card" 
              v-for="item in sortedOfflineList" 
              :key="item.id"
              @tap="viewPlaceDetail(item)"
            >
              <view class="card-header">
                <text class="place-name">{{ item.name }}</text>
                <view class="place-tags">
                  <text class="tag" v-if="item.isTouristSpot">热门打卡</text>
                  <text class="tag brand-tag">{{ item.categoryName || '特色街区' }}</text>
                </view>
              </view>
              
              <view class="place-info">
                <view class="info-row">
                  <image class="info-icon" src="/static/icons/general/location.png" mode="aspectFit"></image>
                  <text class="info-text">{{ item.address }}</text>
                </view>
                <view class="info-row">
                  <image class="info-icon" src="/static/icons/general/distance.png" mode="aspectFit"></image>
                  <text class="info-text">{{ item.distance }}</text>
                </view>
              </view>

              <view class="detail-section" v-if="item.openingHours || item.phone">
                <view class="detail-item" v-if="item.openingHours">
                  <text class="detail-label">开放时间</text>
                  <text class="detail-value">{{ item.openingHours }}</text>
                </view>
                <view class="detail-item" v-if="item.phone">
                  <text class="detail-label">咨询电话</text>
                  <text class="detail-value">{{ item.phone }}</text>
                </view>
              </view>

              <view class="card-actions">
                <view class="action-btn nav" @tap.stop="navigateToPlace(item)">
                  <image class="action-icon" src="/static/icons/general/navigation.png" mode="aspectFit"></image>
                  <text>导航</text>
                </view>
                <view class="action-btn call" @tap.stop="callPlace(item)">
                  <image class="action-icon" src="/static/icons/general/call.png" mode="aspectFit"></image>
                  <text>电话</text>
                </view>
                <view class="action-btn fav" @tap.stop="toggleFavorite(item)">
                  <image 
                    class="action-icon" 
                    :src="item.isFavorite ? '/static/icons/general/heart-filled.png' : '/static/icons/general/heart.png'" 
                    mode="aspectFit"
                  ></image>
                  <text>收藏</text>
                </view>
              </view>
            </view>
          </view>

          <view v-if="offlineLoading && offlineList.length === 0" class="loading-container">
            <text class="loading-text">正在搜索特色街区...</text>
          </view>
          <view v-else-if="!offlineLoading && offlineList.length === 0" class="empty-container">
            <image class="empty-icon" src="/static/icons/general/empty.png" mode="aspectFit"></image>
            <text class="empty-text">未找到相关街区</text>
            <text class="empty-sub">尝试切换关键词</text>
          </view>

          <view class="load-more" v-if="offlineHasMore && offlineList.length > 0">
            <text>{{ offlineLoadingMore ? '加载中...' : '上拉加载更多' }}</text>
          </view>
          <view class="load-more" v-else-if="!offlineHasMore && offlineList.length > 0">
            <text>已加载全部场所</text>
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
          <text class="permission-text">为了提供精准的附近购物场所推荐，需要获取您的位置信息</text>
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
// 腾讯地图API配置（与gas-station一致）
const TENCENT_MAP_KEY = '4DYBZ-7QXEC-CWM2S-AXAZR-YLVQF-C6BPY';
const TENCENT_MAP_BASE_URL = 'https://apis.map.qq.com';

export default {
  data() {
    return {
      currentTab: 'online',
      
      // 线上购物相关数据
      onlineKeyword: '',
      activeOnlineCategory: 'all',
      activeOnlineFilter: 'all',
      onlineList: [],
      onlinePage: 1,
      onlineHasMore: true,
      onlineLoading: false,
      onlineLoadingMore: false,
      
      // 线下购物相关数据
      offlineKeyword: '',
      activeOfflineFilter: 'all',
      offlineList: [],
      offlinePage: 1,
      offlineHasMore: true,
      offlineLoading: false,
      offlineLoadingMore: false,
      
      // 分类配置（保留图标）
      onlineCategories: [
        { id: 'all', name: '全部', icon: '/static/icons/shopping/all.png', keyword: '' },
        { id: 'comprehensive', name: '综合商场', icon: '/static/icons/shopping/comprehensive.png', keyword: '购物中心' },
        { id: 'fashion', name: '时尚服饰', icon: '/static/icons/shopping/fashion.png', keyword: '服装城' },
        { id: 'electronics', name: '电子产品', icon: '/static/icons/shopping/electronics.png', keyword: '数码广场' },
        { id: 'home', name: '家居生活', icon: '/static/icons/shopping/home.png', keyword: '家居商场' },
        { id: 'beauty', name: '美妆个护', icon: '/static/icons/shopping/beauty.png', keyword: '美妆店' },
        { id: 'food', name: '食品生鲜', icon: '/static/icons/shopping/food.png', keyword: '生鲜超市' },
        { id: 'specialty', name: '特产礼品', icon: '/static/icons/shopping/specialty.png', keyword: '特产店' }
      ],
      onlineFilters: [
        { type: 'all', name: '智能排序' },
        { type: 'distance', name: '距离最近' }
      ],
      offlineFilters: [
        { type: 'all', name: '智能排序' },
        { type: 'distance', name: '距离最近' }
      ],
      
      // 位置信息
      currentLocation: {
        latitude: null,
        longitude: null,
        city: ''
      },
      
      favoriteIds: [],
      showPermissionModal: false,
      searchTimer: null
    }
  },
  
  computed: {
    // 线上列表排序（按距离）
    sortedOnlineList() {
      let list = [...this.onlineList];
      if (this.activeOnlineFilter === 'distance') {
        list.sort((a, b) => (a.distanceValue || 0) - (b.distanceValue || 0));
      }
      return list;
    },
    
    // 线下列表排序
    sortedOfflineList() {
      let list = [...this.offlineList];
      if (this.activeOfflineFilter === 'distance') {
        list.sort((a, b) => (a.distanceValue || 0) - (b.distanceValue || 0));
      }
      return list;
    }
  },
  
  onLoad() {
    this.loadFavorites();
    this.getUserLocationAndInit();
  },
  
  methods: {
    // 收藏相关
    loadFavorites() {
      try {
        const favorites = uni.getStorageSync('shopping_favorites');
        if (favorites && Array.isArray(favorites)) {
          this.favoriteIds = favorites;
        }
      } catch(e) {}
    },
    
    saveFavorites() {
      try {
        uni.setStorageSync('shopping_favorites', this.favoriteIds);
      } catch(e) {}
    },
    
    // 定位与初始化
    getUserLocationAndInit() {
      uni.getLocation({
        type: 'gcj02',
        success: (res) => {
          this.currentLocation.latitude = res.latitude;
          this.currentLocation.longitude = res.longitude;
          this.initTabData();
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
          this.initTabData();
        } else {
          throw new Error('IP定位无结果');
        }
      } catch (error) {
        console.error('IP定位失败:', error);
        this.showPermissionModal = true;
      }
    },
    
    initTabData() {
      // 初始化两个tab的数据
      this.resetOnlineData();
      this.resetOfflineData();
    },
    
    // 重置线上数据
    resetOnlineData() {
      this.onlineList = [];
      this.onlinePage = 1;
      this.onlineHasMore = true;
      this.onlineKeyword = '';
      this.activeOnlineCategory = 'all';
      this.loadOnlinePlaces(true);
    },
    
    // 重置线下数据
    resetOfflineData() {
      this.offlineList = [];
      this.offlinePage = 1;
      this.offlineHasMore = true;
      this.offlineKeyword = '';
      this.loadOfflinePlaces(true);
    },
    
    // 加载线上购物场所（商场/购物中心）
    async loadOnlinePlaces(reset = false) {
      if (!this.currentLocation.latitude || !this.currentLocation.longitude) return;
      if (reset) {
        this.onlinePage = 1;
        this.onlineHasMore = true;
        this.onlineLoading = true;
        this.onlineList = [];
      } else {
        if (this.onlineLoadingMore || !this.onlineHasMore) return;
        this.onlineLoadingMore = true;
      }
      
      // 构建搜索关键词
      let keyword = '购物中心';
      if (this.onlineKeyword && this.onlineKeyword.trim()) {
        keyword = this.onlineKeyword.trim();
      } else if (this.activeOnlineCategory !== 'all') {
        const category = this.onlineCategories.find(c => c.id === this.activeOnlineCategory);
        if (category && category.keyword) keyword = category.keyword;
      }
      
      const params = {
        key: TENCENT_MAP_KEY,
        boundary: `nearby(${this.currentLocation.latitude},${this.currentLocation.longitude},5000)`,
        keyword: keyword,
        page_size: 20,
        page_index: this.onlinePage,
        order_by: '_distance'
      };
      
      try {
        const res = await this.requestAPI(`${TENCENT_MAP_BASE_URL}/ws/place/v1/search`, params);
        if (res.status === 0 && res.data && res.data.length) {
          const newPlaces = this.parsePlacesFromAPI(res.data, 'online');
          if (reset) {
            this.onlineList = newPlaces;
          } else {
            this.onlineList = [...this.onlineList, ...newPlaces];
          }
          const total = res.count || 0;
          const loadedCount = this.onlinePage * params.page_size;
          this.onlineHasMore = loadedCount < total && newPlaces.length === params.page_size;
          if (this.onlineHasMore) this.onlinePage++;
        } else {
          if (this.onlinePage === 1) {
            this.onlineList = [];
          }
          this.onlineHasMore = false;
        }
      } catch (error) {
        console.error('请求购物场所失败:', error);
        uni.showToast({ title: '网络错误，请稍后重试', icon: 'none' });
      } finally {
        this.onlineLoading = false;
        this.onlineLoadingMore = false;
      }
    },
    
    // 加载线下购物场所（步行街/特色街区）
    async loadOfflinePlaces(reset = false) {
      if (!this.currentLocation.latitude || !this.currentLocation.longitude) return;
      if (reset) {
        this.offlinePage = 1;
        this.offlineHasMore = true;
        this.offlineLoading = true;
        this.offlineList = [];
      } else {
        if (this.offlineLoadingMore || !this.offlineHasMore) return;
        this.offlineLoadingMore = true;
      }
      
      let keyword = this.offlineKeyword && this.offlineKeyword.trim() 
        ? this.offlineKeyword.trim() 
        : '步行街|特色街区';
      
      const params = {
        key: TENCENT_MAP_KEY,
        boundary: `nearby(${this.currentLocation.latitude},${this.currentLocation.longitude},5000)`,
        keyword: keyword,
        page_size: 20,
        page_index: this.offlinePage,
        order_by: '_distance'
      };
      
      try {
        const res = await this.requestAPI(`${TENCENT_MAP_BASE_URL}/ws/place/v1/search`, params);
        if (res.status === 0 && res.data && res.data.length) {
          const newPlaces = this.parsePlacesFromAPI(res.data, 'offline');
          if (reset) {
            this.offlineList = newPlaces;
          } else {
            this.offlineList = [...this.offlineList, ...newPlaces];
          }
          const total = res.count || 0;
          const loadedCount = this.offlinePage * params.page_size;
          this.offlineHasMore = loadedCount < total && newPlaces.length === params.page_size;
          if (this.offlineHasMore) this.offlinePage++;
        } else {
          if (this.offlinePage === 1) this.offlineList = [];
          this.offlineHasMore = false;
        }
      } catch (error) {
        console.error('请求特色街区失败:', error);
        uni.showToast({ title: '网络错误，请稍后重试', icon: 'none' });
      } finally {
        this.offlineLoading = false;
        this.offlineLoadingMore = false;
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
    
    parsePlacesFromAPI(data, type) {
      return data.map((poi, index) => {
        // 提取营业时间
        let openingHours = '';
        let is24h = false;
        if (poi.opening_hours) {
          const hours = poi.opening_hours;
          if (hours.includes('24小时') || hours.includes('00:00-24:00')) {
            is24h = true;
            openingHours = '24小时营业';
          } else {
            openingHours = hours.length > 30 ? hours.substring(0, 30) + '...' : hours;
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
        
        // 判断是否有优惠活动（根据类别简单判断）
        let hasDiscount = false;
        if (poi.category && (poi.category.includes('折扣') || poi.category.includes('促销'))) {
          hasDiscount = true;
        }
        
        // 判断是否为热门打卡地（根据类别）
        let isTouristSpot = false;
        if (type === 'offline' && (poi.category && (poi.category.includes('旅游') || poi.category.includes('景点')))) {
          isTouristSpot = true;
        }
        
        // 提取品牌或分类名称
        let categoryName = '购物场所';
        if (poi.category) {
          const cats = poi.category.split(',');
          categoryName = cats[cats.length - 1] || '购物';
        }
        
        return {
          id: poi.id || `temp_${Date.now()}_${index}`,
          name: poi.title || '未知场所',
          address: poi.address || poi.location?.address || '地址待补充',
          distance: distance,
          distanceValue: distanceValue,
          phone: poi.tel || '',
          latitude: poi.location?.lat || 0,
          longitude: poi.location?.lng || 0,
          openingHours: openingHours,
          is24h: is24h,
          hasDiscount: hasDiscount,
          isTouristSpot: isTouristSpot,
          categoryName: categoryName,
          isFavorite: this.favoriteIds.includes(poi.id),
          rawPoi: poi
        };
      });
    },
    
    // 切换tab
    switchTab(tab) {
      this.currentTab = tab;
      // 如果当前tab没有数据且定位已有，则加载
      if (tab === 'online' && this.onlineList.length === 0 && this.currentLocation.latitude) {
        this.loadOnlinePlaces(true);
      } else if (tab === 'offline' && this.offlineList.length === 0 && this.currentLocation.latitude) {
        this.loadOfflinePlaces(true);
      }
    },
    
    // 线上搜索
    searchOnline() {
      if (this.searchTimer) clearTimeout(this.searchTimer);
      this.searchTimer = setTimeout(() => {
        this.loadOnlinePlaces(true);
      }, 300);
    },
    
    // 线下搜索
    searchOffline() {
      if (this.searchTimer) clearTimeout(this.searchTimer);
      this.searchTimer = setTimeout(() => {
        this.loadOfflinePlaces(true);
      }, 300);
    },
    
    // 线上分类切换
    onOnlineCategoryChange(categoryId) {
      this.activeOnlineCategory = categoryId;
      this.loadOnlinePlaces(true);
    },
    
    // 线上筛选
    onOnlineFilterChange(filterType) {
      this.activeOnlineFilter = filterType;
    },
    
    // 线下筛选
    onOfflineFilterChange(filterType) {
      this.activeOfflineFilter = filterType;
    },
    
    // 上拉加载更多
    loadMoreOnline() {
      if (!this.onlineHasMore || this.onlineLoadingMore || this.onlineLoading) return;
      this.loadOnlinePlaces(false);
    },
    
    loadMoreOffline() {
      if (!this.offlineHasMore || this.offlineLoadingMore || this.offlineLoading) return;
      this.loadOfflinePlaces(false);
    },
    
    // 查看详情（跳转）
    viewPlaceDetail(item) {
      uni.navigateTo({
        url: `/pages/shopping/place-detail?id=${item.id}&name=${encodeURIComponent(item.name)}&lat=${item.latitude}&lng=${item.longitude}`
      });
    },
    
    // 导航
    navigateToPlace(item) {
      if (item.latitude && item.longitude) {
        uni.openLocation({
          latitude: item.latitude,
          longitude: item.longitude,
          name: item.name,
          address: item.address
        });
      } else {
        uni.showToast({ title: '坐标信息缺失', icon: 'none' });
      }
    },
    
    // 拨打电话
    callPlace(item) {
      if (item.phone) {
        uni.makePhoneCall({ phoneNumber: item.phone });
      } else {
        uni.showToast({ title: '暂无联系电话', icon: 'none' });
      }
    },
    
    // 收藏/取消收藏
    toggleFavorite(item) {
      const index = this.favoriteIds.indexOf(item.id);
      if (index === -1) {
        this.favoriteIds.push(item.id);
        item.isFavorite = true;
        uni.showToast({ title: '已收藏', icon: 'success' });
      } else {
        this.favoriteIds.splice(index, 1);
        item.isFavorite = false;
        uni.showToast({ title: '已取消收藏', icon: 'success' });
      }
      this.saveFavorites();
      
      // 同步更新对应列表中的收藏状态
      if (this.currentTab === 'online') {
        const target = this.onlineList.find(p => p.id === item.id);
        if (target) target.isFavorite = item.isFavorite;
      } else {
        const target = this.offlineList.find(p => p.id === item.id);
        if (target) target.isFavorite = item.isFavorite;
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
            uni.showToast({ title: '权限已开启，重新定位中', icon: 'success' });
            setTimeout(() => {
              this.getUserLocationAndInit();
            }, 1000);
          }
        },
        fail: () => {
          uni.showToast({ title: '打开设置失败', icon: 'none' });
        }
      });
    }
  },
  
  // 监听滚动到底部
  onReachBottom() {
    if (this.currentTab === 'online') {
      this.loadMoreOnline();
    } else {
      this.loadMoreOffline();
    }
  }
}
</script>

<style scoped>
.shopping-page {
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
}

/* 内容区域 */
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

/* 搜索框 */
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

/* 购物卡片样式（类似加油站但适配购物） */
.shopping-list {
  padding: 0 30rpx 30rpx;
}

.shopping-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fbff 100%);
  border-radius: 24rpx;
  overflow: hidden;
  margin-top: 30rpx;
  box-shadow: 0 6rpx 20rpx rgba(184, 212, 255, 0.3);
  border: 1rpx solid #e0e8ff;
  transition: all 0.3s ease;
  padding: 30rpx;
}

.shopping-card:active {
  transform: translateY(4rpx);
  box-shadow: 0 2rpx 10rpx rgba(184, 212, 255, 0.2);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20rpx;
}

.place-name {
  font-size: 34rpx;
  font-weight: 700;
  color: #3a5bc7;
  flex: 1;
  margin-right: 20rpx;
}

.place-tags {
  display: flex;
  gap: 10rpx;
  flex-wrap: wrap;
}

.tag {
  font-size: 20rpx;
  padding: 6rpx 12rpx;
  border-radius: 12rpx;
  background: #e8f1ff;
  color: #5a7bdb;
}

.discount-tag {
  background: #fff0e0;
  color: #ff9a3c;
}

.brand-tag {
  background: #e8f1ff;
  color: #5c9eff;
}

.place-info {
  margin-bottom: 25rpx;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 10rpx;
  margin-bottom: 12rpx;
}

.info-icon {
  width: 24rpx;
  height: 24rpx;
}

.info-text {
  font-size: 24rpx;
  color: #666;
}

.detail-section {
  background: #f8fbff;
  border-radius: 16rpx;
  padding: 20rpx;
  margin-bottom: 25rpx;
  border: 1rpx solid #e8f1ff;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12rpx;
}

.detail-item:last-child {
  margin-bottom: 0;
}

.detail-label {
  font-size: 24rpx;
  color: #999;
}

.detail-value {
  font-size: 24rpx;
  color: #333;
  font-weight: 500;
  text-align: right;
  flex: 1;
  margin-left: 20rpx;
}

.card-actions {
  display: flex;
  gap: 15rpx;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  gap: 8rpx;
  padding: 16rpx;
  border-radius: 12rpx;
  font-size: 24rpx;
  transition: all 0.3s ease;
}

.action-btn.nav {
  background: #e8f1ff;
  color: #b8d4ff;
}

.action-btn.call {
  background: #f0f8f0;
  color: #6bcf7f;
}

.action-btn.fav {
  background: #fff0f0;
  color: #ff6b6b;
}

.action-btn:active {
  transform: scale(0.95);
}

.action-icon {
  width: 24rpx;
  height: 24rpx;
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

.empty-icon {
  width: 120rpx;
  height: 120rpx;
  margin-bottom: 20rpx;
  opacity: 0.5;
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

/* 动画 */
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

.shopping-card {
  animation: fadeIn 0.5s ease forwards;
}
</style>