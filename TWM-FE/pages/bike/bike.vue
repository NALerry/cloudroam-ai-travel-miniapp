<template>
  <view class="bike-page">
    <!-- 顶部状态栏 -->
    <view class="status-bar">
      <view class="status-item">
        <image class="status-icon" src="/static/icons/bike/distance.png" mode="aspectFit"></image>
        <text class="status-label">累计骑行</text>
        <text class="status-value">{{ totalDistance }}km</text>
      </view>
      <view class="status-item">
        <image class="status-icon" src="/static/icons/bike/time.png" mode="aspectFit"></image>
        <text class="status-label">骑行时间</text>
        <text class="status-value">{{ totalTime }}小时</text>
      </view>
      <view class="status-item">
        <image class="status-icon" src="/static/icons/bike/calorie.png" mode="aspectFit"></image>
        <text class="status-label">消耗卡路里</text>
        <text class="status-value">{{ totalCalories }}卡</text>
      </view>
    </view>

    <!-- 搜索栏 -->
    <view class="search-section">
      <view class="search-bar">
        <image class="search-icon" src="/static/icons/general/search.png" mode="aspectFit"></image>
        <input 
          class="search-input" 
          placeholder="搜索附近单车或目的地" 
          v-model="searchKeyword"
          @input="onSearchInput"
        />
        <view class="search-cancel" @tap="onSearchCancel" v-if="searchKeyword">
          <image class="cancel-icon" src="/static/icons/general/close.png" mode="aspectFit"></image>
        </view>
      </view>
    </view>

    <!-- 筛选条件 -->
    <view class="filter-section">
      <scroll-view class="filter-scroll" scroll-x :show-scrollbar="false">
        <view 
          class="filter-item" 
          v-for="filter in availableFilters" 
          :key="filter.type"
          :class="{ active: activeFilter === filter.type && (!filter.type === 'brand' || selectedBrand === filter.value) }"
          @tap="onFilterChange(filter)"
        >
          <text>{{ filter.name }}</text>
        </view>
        <view class="filter-brand-selected" v-if="activeFilter === 'type' && selectedBikeTypeName">
          <text class="brand-name">{{ selectedBikeTypeName }}</text>
          <text class="brand-clear" @tap.stop="clearTypeFilter">✕</text>
        </view>
      </scroll-view>
    </view>

    <!-- 附近单车列表 -->
    <view class="nearby-bikes-section">
      <view class="section-header">
        <text class="section-title">附近单车</text>
        <view class="section-actions">
          <text class="bike-count">{{ filteredBikes.length }}辆可用</text>
          <view class="refresh-btn" @tap="refreshBikeData">
            <image class="refresh-icon" src="/static/icons/general/refresh.png" mode="aspectFit"></image>
            <text>刷新</text>
          </view>
        </view>
      </view>
      
      <scroll-view 
        class="bikes-grid" 
        scroll-y 
        @scrolltolower="loadMore"
        :refresher-enabled="true"
        :refresher-triggered="refreshing"
        @refresherrefresh="onRefresh"
      >
        <view v-if="loading && bikesAll.length === 0" class="loading-container">
          <text class="loading-text">正在获取附近单车...</text>
        </view>

        <view v-else-if="filteredBikes.length === 0 && !loading" class="empty-container">
          <image class="empty-icon" src="/static/icons/general/empty.png" mode="aspectFit"></image>
          <text class="empty-text">没有找到单车</text>
          <text class="empty-sub">尝试切换筛选条件或搜索其他地点</text>
        </view>

        <view 
          class="bike-card" 
          v-for="bike in filteredBikes" 
          :key="bike.id"
          :class="{ selected: selectedBikeId === bike.id }"
          @tap="selectBike(bike)"
        >
          <view class="bike-header">
            <view class="bike-type-info">
              <image class="bike-icon" :src="bike.icon" mode="aspectFit"></image>
              <text class="bike-type">{{ bike.type }}</text>
            </view>
            <view class="bike-status" :class="bike.status">
              <text>{{ bike.statusText }}</text>
            </view>
          </view>
          
          <view class="bike-details">
            <view class="detail-item">
              <image class="detail-icon" src="/static/icons/bike/distance.png" mode="aspectFit"></image>
              <text class="detail-text">{{ bike.distance }}</text>
            </view>
            <view class="detail-item">
              <image class="detail-icon" src="/static/icons/bike/price.png" mode="aspectFit"></image>
              <text class="detail-text">¥{{ bike.price }}/30分钟</text>
            </view>
            <view class="detail-item" v-if="bike.battery">
              <image class="detail-icon" src="/static/icons/bike/battery.png" mode="aspectFit"></image>
              <text class="detail-text">{{ bike.battery }}%电量</text>
            </view>
          </view>
          
          <view class="bike-features">
            <text class="feature-tag" v-for="feature in bike.features" :key="feature">{{ feature }}</text>
          </view>
          
          <view class="bike-actions">
            <view class="action-btn navigate" @tap.stop="navigateToBike(bike)">
              <image class="action-icon" src="/static/icons/general/navigation.png" mode="aspectFit"></image>
              <text>导航</text>
            </view>
            <view class="action-btn rent" @tap.stop="rentBike(bike)">
              <text>立即租用</text>
            </view>
          </view>
        </view>

        <view class="load-more" v-if="hasMore && bikesAll.length > 0">
          <text>{{ loadingMore ? '加载中...' : '加载更多' }}</text>
        </view>
        <view class="load-more" v-else-if="!hasMore && bikesAll.length > 0">
          <text>已加载全部单车</text>
        </view>
      </scroll-view>
    </view>

    <!-- 推荐骑行路线 (图片使用统一占位风格) -->
    <view class="routes-section">
      <view class="section-header">
        <text class="section-title">推荐骑行路线</text>
        <view class="more-btn" @tap="viewMoreRoutes">
          <text>更多</text>
          <image class="more-icon" src="/static/icons/general/more.png" mode="aspectFit"></image>
        </view>
      </view>
      
      <scroll-view class="routes-scroll" scroll-x :show-scrollbar="false">
        <view v-if="recommendedRoutesLoading" class="routes-loading">
          <text>加载推荐路线中...</text>
        </view>
        <view 
          class="route-card" 
          v-for="route in recommendedRoutes" 
          :key="route.id"
          @tap="selectRoute(route)"
          v-else
        >
          <!-- 图片占位区 - 统一使用路线页面的景点图片风格 -->
          <view class="route-image-placeholder">
            <view class="placeholder-icon">🚴‍♂️</view>
            <view class="route-tags">
              <text class="route-tag">{{ route.themeTag || '骑行路线' }}</text>
              <text class="route-tag difficulty-tag" :class="route.difficulty">{{ route.difficultyText }}</text>
            </view>
          </view>

          <view class="route-content">
            <text class="route-name">{{ route.name }}</text>
            <view class="route-meta">
              <view class="meta-item">
                <image class="meta-icon" src="/static/icons/bike/distance.png" mode="aspectFit"></image>
                <text>{{ route.distance }}</text>
              </view>
              <view class="meta-item">
                <image class="meta-icon" src="/static/icons/bike/time.png" mode="aspectFit"></image>
                <text>{{ route.time }}</text>
              </view>
              <view class="meta-item">
                <text class="difficulty" :class="route.difficulty">{{ route.difficultyText }}</text>
              </view>
            </view>
            <text class="route-desc">{{ route.description }}</text>
            <view class="route-stats">
              <view class="stat-item">
                <image class="stat-icon" src="/static/icons/general/star.png" mode="aspectFit"></image>
                <text>{{ route.rating }}</text>
              </view>
              <view class="stat-item">
                <image class="stat-icon" src="/static/icons/general/user.png" mode="aspectFit"></image>
                <text>{{ route.riders }}人骑行</text>
              </view>
            </view>
          </view>
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
          <text class="permission-text">为了提供精准的附近单车服务，需要获取您的位置信息</text>
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
// 腾讯地图API配置（与加油站一致）
const TENCENT_MAP_KEY = '4DYBZ-7QXEC-CWM2S-AXAZR-YLVQF-C6BPY';
const TENCENT_MAP_BASE_URL = 'https://apis.map.qq.com';

export default {
  data() {
    return {
      searchKeyword: '',
      activeFilter: 'all',
      selectedBikeType: 'all',
      selectedBikeTypeName: '',
      availableFilters: [
        { type: 'all', name: '全部' },
        { type: 'nearby', name: '最近' },
        { type: 'type', name: '车型' }
      ],
      
      // 单车数据
      bikesAll: [],
      currentPage: 1,
      pageSize: 20,
      hasMore: true,
      loading: false,
      loadingMore: false,
      refreshing: false,
      
      // 推荐路线数据
      recommendedRoutes: [],
      recommendedRoutesLoading: false,
      
      // 定位相关
      currentLocation: {
        latitude: null,
        longitude: null,
        city: ''
      },
      
      // 筛选相关
      bikeTypeList: [],
      showPermissionModal: false,
      searchTimer: null,
      
      // 顶部用户统计数据（模拟个人数据，可后续对接真实接口）
      totalDistance: '156.8',
      totalTime: '28.5',
      totalCalories: '3250',
      
      // UI状态
      selectedBikeId: null
    }
  },
  computed: {
    filteredBikes() {
      let bikes = [...this.bikesAll];
      
      // 车型过滤
      if (this.selectedBikeType !== 'all') {
        bikes = bikes.filter(bike => bike.typeId === this.selectedBikeType);
      }
      
      // 排序（距离优先）
      if (this.activeFilter === 'nearby') {
        bikes.sort((a, b) => (a.distanceValue || 0) - (b.distanceValue || 0));
      } else {
        // 默认按距离排序
        bikes.sort((a, b) => (a.distanceValue || 0) - (b.distanceValue || 0));
      }
      
      return bikes;
    }
  },
  onLoad() {
    this.getUserLocationAndLoadBikes();
    this.loadRecommendRoutes();
  },
  methods: {
    // ==================== 定位与初始化 ====================
    getUserLocationAndLoadBikes() {
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
      this.bikesAll = [];
      this.currentPage = 1;
      this.hasMore = true;
      this.searchKeyword = '';
      this.selectedBikeType = 'all';
      this.selectedBikeTypeName = '';
      this.activeFilter = 'all';
      this.loadBikes(true);
    },
    
    // ==================== 附近单车API ====================
    async loadBikes(reset = false) {
      if (!this.currentLocation.latitude || !this.currentLocation.longitude) {
        console.warn('位置未获取');
        return;
      }
      
      if (reset) {
        this.currentPage = 1;
        this.hasMore = true;
        this.loading = true;
        this.bikesAll = [];
      } else {
        if (this.loadingMore || !this.hasMore) return;
        this.loadingMore = true;
      }
      
      // 搜索关键词：默认共享单车，如果用户搜索则使用搜索词
      let keyword = '共享单车';
      if (this.searchKeyword && this.searchKeyword.trim()) {
        keyword = this.searchKeyword.trim();
      }
      
      const params = {
        key: TENCENT_MAP_KEY,
        boundary: `nearby(${this.currentLocation.latitude},${this.currentLocation.longitude},3000)`,
        keyword: keyword,
        page_size: this.pageSize,
        page_index: this.currentPage,
        order_by: '_distance'
      };
      
      try {
        const res = await this.requestAPI(`${TENCENT_MAP_BASE_URL}/ws/place/v1/search`, params);
        if (res.status === 0 && res.data && res.data.length) {
          const newBikes = this.parseBikesFromAPI(res.data);
          if (reset) {
            this.bikesAll = newBikes;
          } else {
            this.bikesAll = [...this.bikesAll, ...newBikes];
          }
          this.updateBikeTypeList();
          
          const total = res.count || 0;
          const loadedCount = this.currentPage * this.pageSize;
          this.hasMore = loadedCount < total && newBikes.length === this.pageSize;
          if (this.hasMore) {
            this.currentPage++;
          }
        } else {
          if (this.currentPage === 1) {
            uni.showToast({
              title: '未找到附近单车',
              icon: 'none'
            });
          }
          this.hasMore = false;
        }
      } catch (error) {
        console.error('请求单车数据失败:', error);
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
    
    parseBikesFromAPI(data) {
      return data.map((poi, index) => {
        const title = poi.title || '';
        // 根据名称判断单车类型
        let type = '共享单车';
        let typeId = 'normal';
        let icon = '/static/icons/bike/bike-normal.png';
        let price = 1.5;
        let battery = null;
        let features = ['轻便', '免押金'];
        
        if (title.includes('电动') || title.includes('电单车') || title.includes('电动车')) {
          type = '电动单车';
          typeId = 'electric';
          icon = '/static/icons/bike/bike-electric.png';
          price = 2.0;
          battery = Math.floor(Math.random() * (95 - 60 + 1)) + 60; // 随机电量60-95%
          features = ['电动助力', '续航50km'];
        } else if (title.includes('山地') || title.includes('越野')) {
          type = '山地车';
          typeId = 'mountain';
          icon = '/static/icons/bike/bike-mountain.png';
          price = 3.0;
          features = ['专业变速', '减震系统'];
        } else if (title.includes('哈啰') || title.includes('美团') || title.includes('青桔')) {
          type = '共享单车';
          typeId = 'normal';
          icon = '/static/icons/bike/bike-normal.png';
          price = 1.5;
          features = ['扫码即骑', '免押金'];
        }
        
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
        
        return {
          id: poi.id || `bike_${Date.now()}_${index}`,
          type: type,
          typeId: typeId,
          icon: icon,
          price: price,
          distance: distance,
          distanceValue: distanceValue,
          battery: battery,
          status: 'available',
          statusText: '可用',
          features: features,
          latitude: poi.location?.lat || 0,
          longitude: poi.location?.lng || 0,
          name: title,
          address: poi.address || '',
          rawPoi: poi
        };
      });
    },
    
    updateBikeTypeList() {
      const types = new Map();
      this.bikesAll.forEach(bike => {
        if (!types.has(bike.typeId)) {
          types.set(bike.typeId, { id: bike.typeId, name: bike.type });
        }
      });
      this.bikeTypeList = Array.from(types.values());
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
    
    // ==================== 推荐骑行路线API（图片改为占位风格） ====================
    async loadRecommendRoutes() {
      if (!this.currentLocation.latitude || !this.currentLocation.longitude) {
        setTimeout(() => {
          if (this.currentLocation.latitude) {
            this.loadRecommendRoutes();
          }
        }, 1000);
        return;
      }
      
      this.recommendedRoutesLoading = true;
      const params = {
        key: TENCENT_MAP_KEY,
        boundary: `nearby(${this.currentLocation.latitude},${this.currentLocation.longitude},5000)`,
        keyword: '骑行路线 公园 绿道',
        page_size: 6,
        page_index: 1,
        order_by: '_distance'
      };
      
      try {
        const res = await this.requestAPI(`${TENCENT_MAP_BASE_URL}/ws/place/v1/search`, params);
        if (res.status === 0 && res.data && res.data.length) {
          this.recommendedRoutes = this.parseRoutesFromAPI(res.data);
        } else {
          // 降级：搜索周边景点作为骑行推荐
          const fallbackParams = {
            ...params,
            keyword: '公园 景区'
          };
          const fallbackRes = await this.requestAPI(`${TENCENT_MAP_BASE_URL}/ws/place/v1/search`, fallbackParams);
          if (fallbackRes.status === 0 && fallbackRes.data && fallbackRes.data.length) {
            this.recommendedRoutes = this.parseRoutesFromAPI(fallbackRes.data);
          }
        }
      } catch (error) {
        console.error('加载推荐路线失败:', error);
      } finally {
        this.recommendedRoutesLoading = false;
      }
    },
    
    parseRoutesFromAPI(data) {
      return data.slice(0, 6).map((poi, index) => {
        const distance = poi._distance ? 
          (poi._distance < 1000 ? `${Math.round(poi._distance)}m` : `${(poi._distance / 1000).toFixed(1)}km`) : '未知';
        
        const distNum = poi._distance || 5000;
        const timeMinutes = Math.round(distNum / 200);
        const timeStr = timeMinutes < 60 ? `${timeMinutes}分钟` : `${Math.floor(timeMinutes / 60)}小时${timeMinutes % 60}分钟`;
        
        const difficulties = ['easy', 'medium', 'medium', 'easy', 'hard'];
        const difficultyTexts = { easy: '简单', medium: '中等', hard: '挑战' };
        const difficulty = difficulties[Math.floor(Math.random() * difficulties.length)];
        
        // 根据POI类别生成主题标签
        let themeTag = '骑行路线';
        const category = poi.category || '';
        if (category.includes('公园')) themeTag = '城市绿道';
        else if (category.includes('湖') || category.includes('湿地')) themeTag = '滨水骑行';
        else if (category.includes('山')) themeTag = '山地越野';
        else if (category.includes('历史') || category.includes('文化')) themeTag = '文化漫游';
        else if (category.includes('景区')) themeTag = '风景名胜';
        
        return {
          id: poi.id || `route_${Date.now()}_${index}`,
          name: poi.title || '骑行路线',
          distance: distance,
          time: timeStr,
          difficulty: difficulty,
          difficultyText: difficultyTexts[difficulty],
          description: poi.address ? `位于${poi.address.substring(0, 20)}` : '适合骑行观光',
          rating: (3.5 + Math.random() * 1.5).toFixed(1),
          riders: Math.floor(Math.random() * 2000) + 100,
          latitude: poi.location?.lat,
          longitude: poi.location?.lng,
          themeTag: themeTag,          // 用于占位区标签
          rawPoi: poi
        };
      });
    },
    
    // ==================== 搜索相关 ====================
    onSearchInput() {
      if (this.searchTimer) clearTimeout(this.searchTimer);
      this.searchTimer = setTimeout(() => {
        this.resetAndLoad();
        this.loadRecommendRoutes();
      }, 500);
    },
    
    onSearchCancel() {
      this.searchKeyword = '';
      this.resetAndLoad();
      this.loadRecommendRoutes();
    },
    
    // ==================== 筛选相关 ====================
    onFilterChange(filter) {
      if (filter.type === 'type') {
        if (this.bikeTypeList.length === 0) {
          uni.showToast({
            title: '暂未获取到车型信息',
            icon: 'none'
          });
          return;
        }
        const typeNames = this.bikeTypeList.map(t => t.name);
        uni.showActionSheet({
          itemList: typeNames,
          success: (res) => {
            const selectedType = this.bikeTypeList[res.tapIndex];
            this.selectedBikeType = selectedType.id;
            this.selectedBikeTypeName = selectedType.name;
            this.activeFilter = 'type';
          },
          fail: () => {}
        });
      } else if (filter.type === 'nearby') {
        this.selectedBikeType = 'all';
        this.selectedBikeTypeName = '';
        this.activeFilter = 'nearby';
      } else {
        this.selectedBikeType = 'all';
        this.selectedBikeTypeName = '';
        this.activeFilter = 'all';
      }
    },
    
    clearTypeFilter() {
      this.selectedBikeType = 'all';
      this.selectedBikeTypeName = '';
      this.activeFilter = 'all';
    },
    
    // ==================== 分页与刷新 ====================
    loadMore() {
      if (!this.hasMore || this.loadingMore || this.loading) return;
      this.loadBikes(false);
    },
    
    onRefresh() {
      this.refreshing = true;
      this.resetAndLoad();
      this.loadRecommendRoutes();
    },
    
    refreshBikeData() {
      this.onRefresh();
    },
    
    // ==================== 单车交互 ====================
    selectBike(bike) {
      this.selectedBikeId = bike.id;
    },
    
    navigateToBike(bike) {
      if (bike.latitude && bike.longitude) {
        uni.openLocation({
          latitude: bike.latitude,
          longitude: bike.longitude,
          name: bike.name || bike.type,
          address: bike.address || `距离${bike.distance}`
        });
      } else {
        uni.showToast({
          title: '坐标信息缺失',
          icon: 'none'
        });
      }
    },
    
    rentBike(bike) {
      uni.showModal({
        title: '租用确认',
        content: `确定租用${bike.type}？\n价格：¥${bike.price}/30分钟\n距离：${bike.distance}`,
        confirmText: '立即租用',
        success: (res) => {
          if (res.confirm) {
            uni.showToast({
              title: '模拟租用成功',
              icon: 'success'
            });
          }
        }
      });
    },
    
    // ==================== 路线交互 ====================
    viewMoreRoutes() {
      uni.showToast({
        title: '更多路线开发中',
        icon: 'none'
      });
    },
    
    selectRoute(route) {
      if (route.latitude && route.longitude) {
        uni.openLocation({
          latitude: route.latitude,
          longitude: route.longitude,
          name: route.name,
          address: route.description
        });
      } else {
        uni.showToast({
          title: '路线详情开发中',
          icon: 'none'
        });
      }
    },
    
    // ==================== 权限弹窗 ====================
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
              this.getUserLocationAndLoadBikes();
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
.bike-page {
  height: 100vh;
  background-color: #f8f8f8;
  display: flex;
  flex-direction: column;
}

/* 顶部状态栏 */
.status-bar {
  background: linear-gradient(135deg, #b8d4ff, #8bb8ff);
  padding: 30rpx;
  display: flex;
  justify-content: space-between;
  border-bottom-left-radius: 30rpx;
  border-bottom-right-radius: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(184, 212, 255, 0.3);
}

.status-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
}

.status-icon {
  width: 40rpx;
  height: 40rpx;
}

.status-label {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.8);
}

.status-value {
  font-size: 28rpx;
  color: #fff;
  font-weight: 600;
}

/* 搜索栏 */
.search-section {
  background: #fff;
  padding: 20rpx 30rpx;
  border-bottom: 1rpx solid #eee;
}

.search-bar {
  display: flex;
  align-items: center;
  background: #f5f5f5;
  border-radius: 25rpx;
  padding: 15rpx 20rpx;
  gap: 15rpx;
}

.search-icon {
  width: 28rpx;
  height: 28rpx;
}

.search-input {
  flex: 1;
  font-size: 28rpx;
  color: #333;
}

.search-cancel {
  width: 32rpx;
  height: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cancel-icon {
  width: 20rpx;
  height: 20rpx;
}

/* 筛选栏 */
.filter-section {
  background: #fff;
  padding: 20rpx 30rpx;
  border-bottom: 1rpx solid #eee;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.filter-scroll {
  white-space: nowrap;
  flex: 1;
}

.filter-item {
  display: inline-flex;
  align-items: center;
  padding: 12rpx 24rpx;
  background: #f5f5f5;
  border-radius: 25rpx;
  margin-right: 20rpx;
  font-size: 24rpx;
  color: #666;
  transition: all 0.3s ease;
}

.filter-item.active {
  background: #b8d4ff;
  color: #fff;
}

.filter-brand-selected {
  display: inline-flex;
  align-items: center;
  background: #e8f1ff;
  border-radius: 25rpx;
  padding: 6rpx 16rpx;
  margin-left: 10rpx;
}

.brand-name {
  font-size: 24rpx;
  color: #333;
  margin-right: 8rpx;
}

.brand-clear {
  font-size: 24rpx;
  color: #999;
  padding: 4rpx;
}

/* 附近单车区域 */
.nearby-bikes-section {
  flex: 1;
  background: #fff;
  padding: 30rpx;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25rpx;
  flex-shrink: 0;
}

.section-title {
  font-size: 32rpx;
  color: #333;
  font-weight: 600;
}

.section-actions {
  display: flex;
  align-items: center;
  gap: 15rpx;
}

.bike-count {
  font-size: 24rpx;
  color: #b8d4ff;
  background: #f0f7ff;
  padding: 6rpx 12rpx;
  border-radius: 12rpx;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 6rpx;
  font-size: 24rpx;
  color: #999;
}

.refresh-icon {
  width: 24rpx;
  height: 24rpx;
}

.bikes-grid {
  flex: 1;
  height: 0;
}

.bike-card {
  background: #f8f8f8;
  border-radius: 20rpx;
  padding: 25rpx;
  margin-bottom: 20rpx;
  border: 2rpx solid transparent;
  transition: all 0.3s ease;
}

.bike-card.selected {
  border-color: #b8d4ff;
  background: #f8fbff;
  box-shadow: 0 4rpx 15rpx rgba(184, 212, 255, 0.3);
}

.bike-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.bike-type-info {
  display: flex;
  align-items: center;
  gap: 15rpx;
}

.bike-icon {
  width: 50rpx;
  height: 50rpx;
}

.bike-type {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
}

.bike-status {
  font-size: 22rpx;
  padding: 6rpx 12rpx;
  border-radius: 12rpx;
}

.bike-status.available {
  background: #e8f7eb;
  color: #6bcf7f;
}

.bike-details {
  display: flex;
  gap: 20rpx;
  margin-bottom: 15rpx;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 6rpx;
}

.detail-icon {
  width: 24rpx;
  height: 24rpx;
}

.detail-text {
  font-size: 22rpx;
  color: #666;
}

.bike-features {
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx;
  margin-bottom: 20rpx;
}

.feature-tag {
  font-size: 20rpx;
  color: #b8d4ff;
  background: rgba(184, 212, 255, 0.2);
  padding: 6rpx 10rpx;
  border-radius: 8rpx;
  border: 1rpx solid rgba(184, 212, 255, 0.3);
}

.bike-actions {
  display: flex;
  gap: 15rpx;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  padding: 16rpx;
  border-radius: 12rpx;
  font-size: 24rpx;
  transition: all 0.3s ease;
}

.action-btn.navigate {
  background: #f0f7ff;
  color: #b8d4ff;
}

.action-btn.rent {
  background: #b8d4ff;
  color: #fff;
  font-weight: 500;
}

.action-btn:active {
  transform: scale(0.95);
}

.action-icon {
  width: 20rpx;
  height: 20rpx;
}

/* 推荐路线区域 */
.routes-section {
  background: #fff;
  padding: 30rpx;
  border-top: 1rpx solid #eee;
  margin-top: 20rpx;
}

.more-btn {
  display: flex;
  align-items: center;
  gap: 6rpx;
  font-size: 24rpx;
  color: #b8d4ff;
}

.more-icon {
  width: 20rpx;
  height: 20rpx;
}

.routes-scroll {
  white-space: nowrap;
}

.routes-loading {
  text-align: center;
  padding: 40rpx;
  color: #999;
  font-size: 26rpx;
}

.route-card {
  display: inline-flex;
  background: #f8f8f8;
  border-radius: 20rpx;
  overflow: hidden;
  margin-right: 20rpx;
  width: 300rpx;
}

/* 统一图片占位区 - 与路线页面景点图片风格一致 */
.route-image-placeholder {
  position: relative;
  width: 120rpx;
  height: 140rpx;
  flex-shrink: 0;
  background: linear-gradient(135deg, #e0f0ff 0%, #c8e0ff 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.placeholder-icon {
  font-size: 48rpx;
  opacity: 0.7;
  margin-bottom: 8rpx;
}

.route-tags {
  position: absolute;
  top: 12rpx;
  left: 12rpx;
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.route-tag {
  background: rgba(184, 212, 255, 0.9);
  color: #fff;
  padding: 4rpx 8rpx;
  border-radius: 6rpx;
  font-size: 18rpx;
  white-space: nowrap;
  max-width: 100rpx;
  overflow: hidden;
  text-overflow: ellipsis;
}

.route-tag.difficulty-tag {
  background: rgba(0, 0, 0, 0.6);
}

.route-tag.difficulty-tag.easy {
  background: #6bcf7f;
}

.route-tag.difficulty-tag.medium {
  background: #ffb400;
}

.route-tag.difficulty-tag.hard {
  background: #ff6b6b;
}

.route-content {
  flex: 1;
  padding: 20rpx;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.route-name {
  font-size: 26rpx;
  color: #333;
  font-weight: 500;
  display: block;
  margin-bottom: 10rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.route-meta {
  display: flex;
  gap: 10rpx;
  margin-bottom: 8rpx;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4rpx;
  font-size: 20rpx;
  color: #666;
}

.meta-icon {
  width: 18rpx;
  height: 18rpx;
}

.difficulty {
  font-size: 18rpx;
  padding: 2rpx 6rpx;
  border-radius: 6rpx;
}

.difficulty.easy {
  background: #e8f7eb;
  color: #6bcf7f;
}

.difficulty.medium {
  background: #fff7e6;
  color: #ffb400;
}

.difficulty.hard {
  background: #ffeaea;
  color: #ff6b6b;
}

.route-desc {
  font-size: 20rpx;
  color: #999;
  margin-bottom: 10rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.route-stats {
  display: flex;
  gap: 15rpx;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4rpx;
  font-size: 18rpx;
  color: #999;
}

.stat-icon {
  width: 16rpx;
  height: 16rpx;
}

/* 加载和空状态 */
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

.load-more {
  text-align: center;
  padding: 30rpx;
  color: #b8d4ff;
  font-size: 26rpx;
}

.safe-area {
  height: env(safe-area-inset-bottom);
  background: #f8f8f8;
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
  color: #b8d4ff;
  font-weight: 500;
}

.permission-btn:active {
  background: #f5f5f5;
}
</style>