<!-- route.vue -->
<template>
  <view class="route-page">
    <!-- 搜索栏 -->
    <view class="search-section">
      <view class="search-bar">
        <image class="search-icon" src="/static/icons/general/search.png" mode="aspectFit"></image>
        <input 
          class="search-input" 
          placeholder="搜索景点或目的地" 
          v-model="searchKeyword"
          @input="onSearchInput"
        />
        <view class="search-cancel" @tap="onSearchCancel" v-if="searchKeyword">
          <image class="cancel-icon" src="/static/icons/general/close.png" mode="aspectFit"></image>
        </view>
      </view>
    </view>

    <!-- 筛选栏 -->
    <view class="filter-section">
      <scroll-view class="filter-scroll" scroll-x :show-scrollbar="false">
        <view 
          class="filter-tag" 
          v-for="tag in filterTags" 
          :key="tag.id"
          :class="{ active: selectedFilter === tag.id }"
          @tap="selectFilter(tag.id)"
        >
          <text>{{ tag.name }}</text>
        </view>
      </scroll-view>
    </view>

    <!-- 排序栏 -->
    <view class="sort-bar">
      <view class="sort-btn" @tap="showSortOptions = !showSortOptions">
        <text>{{ sortOptions.find(opt => opt.id === selectedSort)?.name }}</text>
        <image class="sort-icon" src="/static/icons/general/down.png" mode="aspectFit"></image>
      </view>
      <view class="sort-dropdown" v-if="showSortOptions">
        <view 
          class="sort-option" 
          v-for="option in sortOptions" 
          :key="option.id"
          :class="{ active: selectedSort === option.id }"
          @tap="selectSort(option.id)"
        >
          <text>{{ option.name }}</text>
          <image 
            v-if="selectedSort === option.id" 
            class="check-icon" 
            src="/static/icons/general/check.png" 
            mode="aspectFit"
          ></image>
        </view>
      </view>
    </view>

    <!-- 景点列表 -->
    <view class="content-section">
      <scroll-view 
        class="spots-list" 
        scroll-y 
        @scrolltolower="loadMore"
        :refresher-enabled="true"
        :refresher-triggered="refreshing"
        @refresherrefresh="onRefresh"
      >
        <view v-if="loading && spotsAll.length === 0" class="loading-container">
          <text class="loading-text">正在获取附近景点...</text>
        </view>

        <view v-else-if="filteredSpots.length === 0 && !loading" class="empty-container">
          <image class="empty-icon" src="/static/icons/general/empty.png" mode="aspectFit"></image>
          <text class="empty-text">没有找到相关景点</text>
          <text class="empty-sub">尝试切换筛选条件或搜索关键词</text>
        </view>

        <view 
          class="spot-card" 
          v-for="spot in filteredSpots" 
          :key="spot.id"
          @tap="viewSpotDetail(spot)"
        >
          <!-- 无图片占位区域 -->
          <view class="spot-image-placeholder">
            <view class="placeholder-icon">🏞️</view>
            <view class="spot-tags">
              <view class="spot-tag">{{ spot.theme }}</view>
              <view class="spot-tag price-tag" v-if="spot.priceInfo">{{ spot.priceInfo }}</view>
            </view>
            <view class="favorite-btn" @tap.stop="toggleFavorite(spot)">
              <image 
                class="favorite-icon" 
                :src="spot.isFavorite ? '/static/icons/general/heart-filled.png' : '/static/icons/general/heart.png'" 
                mode="aspectFit"
              ></image>
            </view>
          </view>

          <view class="spot-content">
            <view class="spot-header">
              <text class="spot-title">{{ spot.name }}</text>
              <view class="spot-rating" v-if="spot.rating">
                <image class="star-icon" src="/static/icons/general/star.png" mode="aspectFit"></image>
                <text class="rating-score">{{ spot.rating }}</text>
              </view>
            </view>

            <view class="spot-meta">
              <text class="meta-text">{{ spot.suggestedDuration }}</text>
              <text class="meta-sep"> </text>
              <text class="meta-text">{{ spot.distance || '距离未知' }}</text>
              <text class="meta-sep"> </text>
              <text class="meta-text">{{ spot.referenceCost }}</text>
            </view>

            <view class="spot-desc">
              <text class="desc-text">{{ spot.address || spot.description || '暂无详细介绍' }}</text>
            </view>

            <view class="spot-highlights">
              <text class="highlights-title">推荐亮点：</text>
              <text class="highlights-text">{{ spot.highlights || getDefaultHighlights(spot) }}</text>
            </view>

            <view class="spot-actions">
              <view class="action-btn add" @tap.stop="addToTempRoute(spot)">
                <image class="action-icon" src="/static/icons/general/add.png" mode="aspectFit"></image>
                <text>添加路线</text>
              </view>
              <view class="action-btn navigation" @tap.stop="navigateToSpot(spot)">
                <image class="action-icon" src="/static/icons/general/navigation.png" mode="aspectFit"></image>
                <text>导航</text>
              </view>
            </view>
          </view>
        </view>

        <view class="load-more" v-if="hasMore && spotsAll.length > 0">
          <text>{{ loadingMore ? '加载中...' : '加载更多' }}</text>
        </view>
        <view class="load-more" v-else-if="!hasMore && spotsAll.length > 0">
          <text>已加载全部景点</text>
        </view>
      </scroll-view>
    </view>

    <!-- 临时路线面板 -->
    <view class="temp-route-panel" v-if="tempRouteSpots.length > 0">
      <view class="panel-header">
        <text class="panel-title">我的路线 ({{ tempRouteSpots.length }}个景点)</text>
        <view class="panel-actions">
          <text class="clear-btn" @tap="clearTempRoute">清空</text>
          <text class="save-btn" @tap="saveRoute">保存路线</text>
        </view>
      </view>
      <scroll-view class="temp-spots-scroll" scroll-x>
        <view class="temp-spots">
          <view 
            class="temp-spot-item" 
            v-for="(spot, index) in tempRouteSpots" 
            :key="spot.id"
          >
            <text class="temp-spot-name">{{ spot.name }}</text>
            <view class="remove-spot" @tap.stop="removeFromTempRoute(index)">✕</view>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 创建路线浮动按钮 -->
    <view class="create-route-fab" @tap="openCreateRouteDialog">
      <image class="fab-icon" src="/static/icons/general/add.png" mode="aspectFit"></image>
      <text class="fab-text">新建路线</text>
    </view>

    <!-- 保存路线对话框 -->
    <view class="dialog-mask" v-if="showSaveDialog" @tap="closeSaveDialog">
      <view class="dialog-content" @tap.stop>
        <view class="dialog-header">
          <text class="dialog-title">保存路线</text>
          <text class="dialog-close" @tap="closeSaveDialog">✕</text>
        </view>
        <view class="dialog-body">
          <input class="route-name-input" placeholder="请输入路线名称" v-model="newRouteName" />
          <view class="route-summary">
            <text>包含景点：{{ tempRouteSpots.length }}个</text>
            <text>预计总花费：¥{{ totalEstimatedCost }}</text>
            <text>预计总时长：{{ totalEstimatedDuration }}</text>
          </view>
        </view>
        <view class="dialog-footer">
          <button class="dialog-btn cancel" @tap="closeSaveDialog">取消</button>
          <button class="dialog-btn confirm" @tap="confirmSaveRoute">保存</button>
        </view>
      </view>
    </view>

    <!-- 定位权限提示 -->
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

    <view class="safe-area"></view>
  </view>
</template>

<script>
// 腾讯地图API配置
const TENCENT_MAP_KEY = '4DYBZ-7QXEC-CWM2S-AXAZR-YLVQF-C6BPY';
const TENCENT_MAP_BASE_URL = 'https://apis.map.qq.com';

// 计算两点间距离（km）
function getDistance(lat1, lng1, lat2, lng2) {
  const radLat1 = lat1 * Math.PI / 180.0;
  const radLat2 = lat2 * Math.PI / 180.0;
  const a = radLat1 - radLat2;
  const b = lng1 * Math.PI / 180.0 - lng2 * Math.PI / 180.0;
  let s = 2 * Math.asin(Math.sqrt(Math.pow(Math.sin(a/2),2) +
    Math.cos(radLat1) * Math.cos(radLat2) * Math.pow(Math.sin(b/2),2)));
  s = s * 6378.137;
  return Math.round(s * 10) / 10;
}

export default {
  data() {
    return {
      searchKeyword: '',
      selectedFilter: 'all',
      selectedSort: 'distance',
      showSortOptions: false,
      filterTags: [
        { id: 'all', name: '全部' },
        { id: 'natural', name: '自然风光' },
        { id: 'cultural', name: '文化古迹' },
        { id: 'urban', name: '城市地标' },
        { id: 'amusement', name: '主题乐园' },
        { id: 'religious', name: '宗教寺庙' },
        { id: 'museum', name: '博物馆' },
        { id: 'park', name: '公园' }
      ],
      sortOptions: [
        { id: 'distance', name: '距离最近' },
        { id: 'rating', name: '评分最高' },
        { id: 'cost', name: '消费最低' }
      ],
      
      spotsAll: [],
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
      
      tempRouteSpots: [],
      favoriteIds: [],
      
      showPermissionModal: false,
      showSaveDialog: false,
      newRouteName: '',
      
      searchTimer: null
    }
  },
  computed: {
    filteredSpots() {
      let spots = [...this.spotsAll];
      
      if (this.searchKeyword && this.searchKeyword.trim()) {
        const keyword = this.searchKeyword.trim().toLowerCase();
        spots = spots.filter(spot => 
          spot.name.toLowerCase().includes(keyword) || 
          (spot.address && spot.address.toLowerCase().includes(keyword))
        );
      }
      
      if (this.selectedFilter !== 'all') {
        spots = spots.filter(spot => spot.themeId === this.selectedFilter);
      }
      
      switch (this.selectedSort) {
        case 'distance':
          spots.sort((a, b) => (a.distanceValue || 0) - (b.distanceValue || 0));
          break;
        case 'rating':
          spots.sort((a, b) => (b.rating || 0) - (a.rating || 0));
          break;
        case 'cost':
          spots.sort((a, b) => (a.costValue || 0) - (b.costValue || 0));
          break;
        default:
          spots.sort((a, b) => (a.distanceValue || 0) - (b.distanceValue || 0));
      }
      
      return spots;
    },
    
    totalEstimatedCost() {
      return this.tempRouteSpots.reduce((sum, spot) => sum + (spot.costValue || 0), 0);
    },
    
    totalEstimatedDuration() {
      const totalHours = this.tempRouteSpots.reduce((sum, spot) => {
        const hours = parseFloat(spot.suggestedDuration) || 1;
        return sum + hours;
      }, 0);
      if (totalHours < 24) return `${totalHours}小时`;
      return `${Math.floor(totalHours / 24)}天${totalHours % 24}小时`;
    }
  },
  onLoad() {
    this.loadFavorites();
    this.getUserLocationAndLoadSpots();
  },
  methods: {
    getUserLocationAndLoadSpots() {
      this.loading = true;
      uni.getLocation({
        type: 'gcj02',
        success: (res) => {
          this.currentLocation.latitude = res.latitude;
          this.currentLocation.longitude = res.longitude;
          this.resetAndLoad();
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
      this.spotsAll = [];
      this.currentPage = 1;
      this.hasMore = true;
      this.loadSpots(true);
    },
    
    async loadSpots(reset = false) {
      if (!this.currentLocation.latitude || !this.currentLocation.longitude) {
        console.warn('位置未获取');
        return;
      }
      
      if (reset) {
        this.currentPage = 1;
        this.hasMore = true;
        this.loading = true;
        this.spotsAll = [];
      } else {
        if (this.loadingMore || !this.hasMore) return;
        this.loadingMore = true;
      }
      
      const keyword = this.searchKeyword && this.searchKeyword.trim() ? this.searchKeyword.trim() : '景点';
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
          const newSpots = this.parseSpotsFromAPI(res.data);
          if (reset) {
            this.spotsAll = newSpots;
          } else {
            this.spotsAll = [...this.spotsAll, ...newSpots];
          }
          
          const total = res.count || 0;
          const loadedCount = this.currentPage * this.pageSize;
          this.hasMore = loadedCount < total && newSpots.length === this.pageSize;
          if (this.hasMore) {
            this.currentPage++;
          }
        } else {
          if (this.currentPage === 1 && !reset) {
            uni.showToast({ title: '未找到相关景点', icon: 'none' });
          }
          this.hasMore = false;
        }
      } catch (error) {
        console.error('请求景点数据失败:', error);
        uni.showToast({ title: '网络错误，请稍后重试', icon: 'none' });
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
    
    parseSpotsFromAPI(data) {
      return data.map((poi, index) => {
        const category = poi.category || '';
        let theme = '旅游景点';
        let themeId = 'all';
        if (category.includes('风景名胜') || category.includes('自然保护') || category.includes('山') || category.includes('湖')) {
          theme = '自然风光';
          themeId = 'natural';
        } else if (category.includes('文物古迹') || category.includes('历史建筑') || category.includes('古镇')) {
          theme = '文化古迹';
          themeId = 'cultural';
        } else if (category.includes('城市广场') || category.includes('地标') || category.includes('商业街')) {
          theme = '城市地标';
          themeId = 'urban';
        } else if (category.includes('主题乐园') || category.includes('游乐场')) {
          theme = '主题乐园';
          themeId = 'amusement';
        } else if (category.includes('寺庙') || category.includes('教堂') || category.includes('宗教')) {
          theme = '宗教寺庙';
          themeId = 'religious';
        } else if (category.includes('博物馆') || category.includes('展览馆')) {
          theme = '博物馆';
          themeId = 'museum';
        } else if (category.includes('公园') || category.includes('园林')) {
          theme = '公园';
          themeId = 'park';
        }
        
        let suggestedHours = 2;
        if (themeId === 'museum') suggestedHours = 3;
        else if (themeId === 'amusement') suggestedHours = 5;
        else if (themeId === 'park') suggestedHours = 1.5;
        else if (themeId === 'natural') suggestedHours = 3;
        
        let costValue = 0;
        let referenceCost = '免费';
        if (themeId === 'amusement') { costValue = 200; referenceCost = '¥200起'; }
        else if (themeId === 'museum') { costValue = 50; referenceCost = '¥50'; }
        else if (themeId === 'cultural') { costValue = 60; referenceCost = '¥60'; }
        else if (themeId === 'religious') { costValue = 20; referenceCost = '¥20'; }
        
        let distance = '';
        let distanceValue = 0;
        if (poi._distance) {
          distanceValue = poi._distance;
          if (poi._distance < 1000) {
            distance = `${Math.round(poi._distance)}m`;
          } else {
            distance = `${(poi._distance / 1000).toFixed(1)}km`;
          }
        }
        
        let rating = null;
        if (poi.overall_rating) {
          rating = poi.overall_rating;
        } else {
          rating = (4.0 + Math.random() * 0.8).toFixed(1);
        }
        
        return {
          id: poi.id || `temp_${Date.now()}_${index}`,
          name: poi.title || '景点',
          address: poi.address || poi.location?.address || '地址信息待补充',
          distance: distance,
          distanceValue: distanceValue,
          latitude: poi.location?.lat || 0,
          longitude: poi.location?.lng || 0,
          theme: theme,
          themeId: themeId,
          suggestedDuration: `${suggestedHours}小时`,
          referenceCost: referenceCost,
          costValue: costValue,
          rating: rating,
          description: poi._describe || `${poi.title}是当地著名景点，值得一游`,
          highlights: this.generateHighlights(poi, theme),
          isFavorite: this.favoriteIds.includes(poi.id),
          rawPoi: poi
        };
      });
    },
    
    generateHighlights(poi, theme) {
      const highlights = [];
      if (poi.title) highlights.push(poi.title);
      highlights.push(theme);
      if (poi.address) highlights.push(poi.address.split(' ')[0]);
      return highlights.join(' · ');
    },
    
    getDefaultHighlights(spot) {
      return `${spot.theme} · 热门打卡地 · 值得游览`;
    },
    
    onSearchInput() {
      if (this.searchTimer) clearTimeout(this.searchTimer);
      this.searchTimer = setTimeout(() => {
        this.resetAndLoad();
      }, 500);
    },
    
    onSearchCancel() {
      this.searchKeyword = '';
      this.resetAndLoad();
    },
    
    selectFilter(filterId) {
      this.selectedFilter = filterId;
      this.showSortOptions = false;
    },
    
    selectSort(sortId) {
      this.selectedSort = sortId;
      this.showSortOptions = false;
    },
    
    loadMore() {
      if (!this.hasMore || this.loadingMore || this.loading) return;
      this.loadSpots(false);
    },
    
    onRefresh() {
      this.refreshing = true;
      this.resetAndLoad();
    },
    
    loadFavorites() {
      try {
        const favorites = uni.getStorageSync('route_favorites');
        if (favorites && Array.isArray(favorites)) {
          this.favoriteIds = favorites;
        }
      } catch(e) {}
    },
    
    saveFavorites() {
      try {
        uni.setStorageSync('route_favorites', this.favoriteIds);
      } catch(e) {}
    },
    
    toggleFavorite(spot) {
      const index = this.favoriteIds.indexOf(spot.id);
      if (index === -1) {
        this.favoriteIds.push(spot.id);
        spot.isFavorite = true;
        uni.showToast({ title: '已收藏', icon: 'success' });
      } else {
        this.favoriteIds.splice(index, 1);
        spot.isFavorite = false;
        uni.showToast({ title: '已取消收藏', icon: 'success' });
      }
      this.saveFavorites();
      const target = this.spotsAll.find(s => s.id === spot.id);
      if (target) target.isFavorite = spot.isFavorite;
    },
    
    addToTempRoute(spot) {
      if (this.tempRouteSpots.some(s => s.id === spot.id)) {
        uni.showToast({ title: '该景点已在路线中', icon: 'none' });
        return;
      }
      this.tempRouteSpots.push({ ...spot });
      uni.showToast({ title: `已添加 ${spot.name}`, icon: 'success' });
    },
    
    removeFromTempRoute(index) {
      const removed = this.tempRouteSpots[index];
      this.tempRouteSpots.splice(index, 1);
      uni.showToast({ title: `已移除 ${removed.name}`, icon: 'none' });
    },
    
    clearTempRoute() {
      if (this.tempRouteSpots.length === 0) return;
      uni.showModal({
        title: '确认清空',
        content: '确定要清空路线中的所有景点吗？',
        success: (res) => {
          if (res.confirm) {
            this.tempRouteSpots = [];
            uni.showToast({ title: '已清空', icon: 'success' });
          }
        }
      });
    },
    
    openCreateRouteDialog() {
      if (this.tempRouteSpots.length === 0) {
        uni.showToast({ title: '请先添加景点', icon: 'none' });
        return;
      }
      this.newRouteName = `我的路线${new Date().toLocaleDateString()}`;
      this.showSaveDialog = true;
    },
    
    closeSaveDialog() {
      this.showSaveDialog = false;
      this.newRouteName = '';
    },
    
    // 计算总距离
    calculateTotalDistance(spots) {
      if (spots.length < 2) return 0;
      let total = 0;
      for (let i = 0; i < spots.length - 1; i++) {
        const s1 = spots[i];
        const s2 = spots[i+1];
        if (s1.latitude && s1.longitude && s2.latitude && s2.longitude) {
          total += getDistance(s1.latitude, s1.longitude, s2.latitude, s2.longitude);
        }
      }
      return Math.round(total * 10) / 10;
    },
    
    // 计算总时长（天数）
    calculateTotalDays(spots) {
      let totalHours = 0;
      for (let spot of spots) {
        let hours = 2;
        if (spot.suggestedDuration) {
          const match = spot.suggestedDuration.match(/(\d+(?:\.\d+)?)/);
          if (match) hours = parseFloat(match[1]);
        }
        totalHours += hours;
      }
      const days = Math.ceil(totalHours / 8);
      return days >= 1 ? days : 1;
    },
    
    confirmSaveRoute() {
      if (!this.newRouteName.trim()) {
        uni.showToast({ title: '请输入路线名称', icon: 'none' });
        return;
      }
      if (this.tempRouteSpots.length === 0) {
        uni.showToast({ title: '请添加景点', icon: 'none' });
        return;
      }
      
      const spots = this.tempRouteSpots;
      const totalDistance = this.calculateTotalDistance(spots);
      const totalDays = this.calculateTotalDays(spots);
      const placesNames = spots.map(s => s.name);
      const coordinates = spots.map(s => ({
        name: s.name,
        latitude: s.latitude,
        longitude: s.longitude,
        address: s.address
      }));
      
      const newRoute = {
        id: Date.now(),
        name: this.newRouteName.trim(),
        description: `包含${spots.length}个景点的旅行路线，总距离${totalDistance}km`,
        places: placesNames,
        duration: totalDays,
        distance: totalDistance,
        tags: ['自定义', '最新'],
        createTime: new Date().toISOString(),
        coordinates: coordinates
      };
      
      try {
        const savedRoutes = uni.getStorageSync('user_routes') || [];
        savedRoutes.unshift(newRoute);
        uni.setStorageSync('user_routes', savedRoutes);
        
        // 通知其他页面刷新
        uni.$emit('routesUpdated');
        
        uni.showToast({ title: '路线保存成功', icon: 'success' });
        this.showSaveDialog = false;
        this.tempRouteSpots = [];
        this.newRouteName = '';
      } catch(e) {
        console.error(e);
        uni.showToast({ title: '保存失败', icon: 'none' });
      }
    },
    
    viewSpotDetail(spot) {
      uni.navigateTo({
        url: `/pages/spot/detail?id=${spot.id}&name=${encodeURIComponent(spot.name)}&lat=${spot.latitude}&lng=${spot.longitude}`
      });
    },
    
    navigateToSpot(spot) {
      if (spot.latitude && spot.longitude) {
        uni.openLocation({
          latitude: spot.latitude,
          longitude: spot.longitude,
          name: spot.name,
          address: spot.address
        });
      } else {
        uni.showToast({ title: '坐标信息缺失', icon: 'none' });
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
              this.getUserLocationAndLoadSpots();
            }, 1000);
          }
        }
      });
    }
  }
}
</script>

<style scoped>
/* 样式保持不变，与之前相同 */
.route-page {
  height: 100vh;
  background-color: #f8f8f8;
  display: flex;
  flex-direction: column;
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
}

.search-icon {
  width: 28rpx;
  height: 28rpx;
  margin-right: 15rpx;
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
}

.filter-scroll {
  white-space: nowrap;
}

.filter-tag {
  display: inline-flex;
  padding: 12rpx 24rpx;
  background: #f5f5f5;
  border-radius: 25rpx;
  margin-right: 20rpx;
  font-size: 24rpx;
  color: #666;
  transition: all 0.3s ease;
}

.filter-tag.active {
  background: #b8d4ff;
  color: #fff;
}

/* 排序栏 */
.sort-bar {
  background: #fff;
  padding: 15rpx 30rpx;
  border-bottom: 1rpx solid #eee;
  position: relative;
}

.sort-btn {
  display: inline-flex;
  align-items: center;
  gap: 8rpx;
  padding: 10rpx 20rpx;
  background: #f5f5f5;
  border-radius: 20rpx;
  font-size: 24rpx;
  color: #666;
}

.sort-icon {
  width: 20rpx;
  height: 20rpx;
}

.sort-dropdown {
  position: absolute;
  top: 60rpx;
  left: 30rpx;
  background: #fff;
  border-radius: 12rpx;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.12);
  z-index: 10;
  overflow: hidden;
}

.sort-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 25rpx;
  min-width: 180rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.sort-option:last-child {
  border-bottom: none;
}

.sort-option.active {
  background: #f8fbff;
  color: #b8d4ff;
}

.check-icon {
  width: 24rpx;
  height: 24rpx;
}

/* 内容区域 */
.content-section {
  flex: 1;
  overflow: hidden;
}

.spots-list {
  height: 100%;
  padding: 20rpx 30rpx;
}

/* 景点卡片 */
.spot-card {
  background: #fff;
  border-radius: 20rpx;
  margin-bottom: 25rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
  overflow: hidden;
  transition: all 0.3s ease;
}

.spot-card:active {
  transform: scale(0.98);
}

/* 占位图片区域 */
.spot-image-placeholder {
  position: relative;
  height: 180rpx;
  background: linear-gradient(135deg, #e0f0ff 0%, #c8e0ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-icon {
  font-size: 64rpx;
  opacity: 0.6;
}

.spot-tags {
  position: absolute;
  top: 20rpx;
  left: 20rpx;
  display: flex;
  gap: 10rpx;
}

.spot-tag {
  background: rgba(184, 212, 255, 0.9);
  color: #fff;
  padding: 6rpx 12rpx;
  border-radius: 8rpx;
  font-size: 20rpx;
}

.spot-tag.price-tag {
  background: rgba(255, 100, 100, 0.9);
}

.favorite-btn {
  position: absolute;
  top: 20rpx;
  right: 20rpx;
  width: 60rpx;
  height: 60rpx;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.favorite-icon {
  width: 28rpx;
  height: 28rpx;
}

/* 卡片内容 - 全部居中 */
.spot-content {
  padding: 25rpx;
  text-align: center;
}

.spot-header {
  display: flex;
  justify-content: center;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-bottom: 20rpx;
}

.spot-title {
  font-size: 32rpx;
  color: #333;
  font-weight: 600;
  line-height: 1.4;
  text-align: center;
}

.spot-rating {
  display: inline-flex;
  align-items: center;
  gap: 6rpx;
  background: rgba(255, 180, 0, 0.1);
  padding: 4rpx 12rpx;
  border-radius: 20rpx;
}

.star-icon {
  width: 24rpx;
  height: 24rpx;
}

.rating-score {
  font-size: 24rpx;
  color: #ffb300;
  font-weight: 600;
}

/* 元信息：纯文本，无图标，居中 */
.spot-meta {
  display: flex;
  justify-content: center;
  gap: 20rpx;
  margin-bottom: 15rpx;
  flex-wrap: wrap;
}

.meta-text {
  font-size: 24rpx;
  color: #666;
}

.spot-desc {
  margin-bottom: 15rpx;
}

.desc-text {
  font-size: 26rpx;
  color: #666;
  line-height: 1.5;
  text-align: center;
  display: inline-block;
  max-width: 90%;
}

.spot-highlights {
  background: #f8fbff;
  padding: 15rpx;
  border-radius: 12rpx;
  margin-bottom: 20rpx;
  text-align: center;
}

.highlights-title {
  font-size: 24rpx;
  color: #b8d4ff;
  font-weight: 500;
  display: inline-block;
  margin-right: 8rpx;
}

.highlights-text {
  font-size: 24rpx;
  color: #666;
  line-height: 1.4;
}

.spot-actions {
  display: flex;
  justify-content: center;
  gap: 30rpx;
  margin-top: 15rpx;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10rpx;
  padding: 16rpx 40rpx;
  border-radius: 50rpx;
  font-size: 26rpx;
  transition: all 0.3s ease;
  min-width: 160rpx;
}

.action-btn.add {
  background: #e8f1ff;
  color: #5c9eff;
}

.action-btn.navigation {
  background: #f0f8f0;
  color: #52c41a;
}

.action-btn:active {
  transform: scale(0.95);
  opacity: 0.8;
}

.action-icon {
  width: 28rpx;
  height: 28rpx;
}

/* 临时路线面板 */
.temp-route-panel {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  border-radius: 30rpx 30rpx 0 0;
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.1);
  padding: 20rpx 30rpx;
  z-index: 50;
  backdrop-filter: blur(10px);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15rpx;
  padding-bottom: 10rpx;
  border-bottom: 1rpx solid #eee;
}

.panel-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
}

.panel-actions {
  display: flex;
  gap: 20rpx;
}

.clear-btn, .save-btn {
  font-size: 24rpx;
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
}

.clear-btn {
  color: #999;
}

.save-btn {
  background: #b8d4ff;
  color: #fff;
}

.temp-spots-scroll {
  white-space: nowrap;
}

.temp-spots {
  display: inline-flex;
  gap: 15rpx;
  padding: 5rpx 0;
}

.temp-spot-item {
  display: inline-flex;
  align-items: center;
  background: #f5f5f5;
  border-radius: 25rpx;
  padding: 10rpx 20rpx;
  gap: 10rpx;
}

.temp-spot-name {
  font-size: 24rpx;
  color: #333;
  max-width: 200rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-spot {
  width: 32rpx;
  height: 32rpx;
  background: #ff6b6b;
  color: #fff;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 20rpx;
}

/* 创建路线按钮 */
.create-route-fab {
  position: fixed;
  right: 30rpx;
  bottom: 140rpx;
  background: linear-gradient(135deg, #b8d4ff 0%, #8bb9ff 100%);
  border-radius: 50rpx;
  padding: 20rpx 30rpx;
  display: flex;
  align-items: center;
  gap: 10rpx;
  box-shadow: 0 6rpx 20rpx rgba(139, 185, 255, 0.4);
  z-index: 60;
}

.fab-icon {
  width: 32rpx;
  height: 32rpx;
}

.fab-text {
  font-size: 26rpx;
  color: #2c5282;
  font-weight: 600;
}

/* 对话框 */
.dialog-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.dialog-content {
  background: #fff;
  border-radius: 20rpx;
  width: 600rpx;
  overflow: hidden;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #eee;
}

.dialog-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
}

.dialog-close {
  font-size: 32rpx;
  color: #999;
}

.dialog-body {
  padding: 30rpx;
}

.route-name-input {
  border: 1rpx solid #eee;
  border-radius: 12rpx;
  padding: 20rpx;
  font-size: 28rpx;
  margin-bottom: 20rpx;
}

.route-summary {
  background: #f8f8f8;
  border-radius: 12rpx;
  padding: 20rpx;
  display: flex;
  flex-direction: column;
  gap: 10rpx;
  font-size: 26rpx;
  color: #666;
  text-align: center;
}

.dialog-footer {
  display: flex;
  border-top: 1rpx solid #eee;
}

.dialog-btn {
  flex: 1;
  text-align: center;
  padding: 30rpx;
  font-size: 28rpx;
  background: none;
  border: none;
}

.dialog-btn.cancel {
  color: #999;
  border-right: 1rpx solid #eee;
}

.dialog-btn.confirm {
  color: #b8d4ff;
  font-weight: 500;
}

/* 其他辅助 */
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
</style>