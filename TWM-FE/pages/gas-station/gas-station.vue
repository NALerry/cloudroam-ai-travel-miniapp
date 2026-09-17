<template>
  <view class="gas-station-page">
    <!-- 搜索栏 -->
    <view class="search-section">
      <view class="search-bar">
        <image class="search-icon" src="/static/icons/general/search.png" mode="aspectFit"></image>
        <input 
          class="search-input" 
          placeholder="搜索加油站" 
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
          :class="{ active: activeFilter === filter.type && (!filter.brandValue || filter.brandValue === selectedBrand) }"
          @tap="onFilterChange(filter)"
        >
          <text>{{ filter.name }}</text>
        </view>
        <view class="filter-brand-selected" v-if="activeFilter === 'brand' && selectedBrand">
          <text class="brand-name">{{ selectedBrand }}</text>
          <text class="brand-clear" @tap.stop="clearBrandFilter">✕</text>
        </view>
      </scroll-view>
    </view>

    <!-- 列表区域 -->
    <view class="content-section">
      <scroll-view 
        class="station-list" 
        scroll-y 
        @scrolltolower="loadMore"
        :refresher-enabled="true"
        :refresher-triggered="refreshing"
        @refresherrefresh="onRefresh"
      >
        <view v-if="loading && stationsAll.length === 0" class="loading-container">
          <text class="loading-text">正在获取附近加油站...</text>
        </view>

        <view v-else-if="filteredStations.length === 0 && !loading" class="empty-container">
          <image class="empty-icon" src="/static/icons/general/empty.png" mode="aspectFit"></image>
          <text class="empty-text">没有找到加油站</text>
          <text class="empty-sub">尝试切换筛选条件或搜索关键词</text>
        </view>

        <view 
          class="station-item" 
          v-for="station in filteredStations" 
          :key="station.id"
          @tap="viewStationDetail(station)"
        >
          <view class="station-header">
            <text class="station-name">{{ station.name }}</text>
            <view class="station-tags">
              <text class="station-tag" v-if="station.is24h">24小时</text>
              <text class="station-tag discount-tag" v-if="station.hasDiscount">优惠</text>
              <text class="station-tag brand-tag">{{ station.brandName || '加油站' }}</text>
            </view>
          </view>
          
          <view class="station-info">
            <view class="info-row">
              <image class="info-icon" src="/static/icons/general/location.png" mode="aspectFit"></image>
              <text class="info-text">{{ station.address }}</text>
            </view>
            <view class="info-row">
              <image class="info-icon" src="/static/icons/general/distance.png" mode="aspectFit"></image>
              <text class="info-text">{{ station.distance }}</text>
            </view>
          </view>

          <view class="price-section">
            <view class="price-item">
              <text class="fuel-type">油价参考</text>
              <text class="price" style="font-size: 22rpx;">实时价以站内为准</text>
            </view>
            <view class="price-item">
              <text class="fuel-type">营业状态</text>
              <text class="price" style="color:#333;">{{ station.openingStatus || '营业中' }}</text>
            </view>
            <view class="price-item" v-if="station.phone">
              <text class="fuel-type">联系电话</text>
              <text class="price" style="font-size: 24rpx;">{{ station.phone }}</text>
            </view>
          </view>

          <view class="station-actions">
            <view class="action-btn navigation" @tap.stop="navigateToStation(station)">
              <image class="action-icon" src="/static/icons/general/navigation.png" mode="aspectFit"></image>
              <text>导航</text>
            </view>
            <view class="action-btn call" @tap.stop="callStation(station)">
              <image class="action-icon" src="/static/icons/general/call.png" mode="aspectFit"></image>
              <text>电话</text>
            </view>
            <view class="action-btn favorite" @tap.stop="toggleFavorite(station)">
              <image 
                class="action-icon" 
                :src="station.isFavorite ? '/static/icons/general/heart-filled.png' : '/static/icons/general/heart.png'" 
                mode="aspectFit"
              ></image>
              <text>收藏</text>
            </view>
          </view>
        </view>

        <view class="load-more" v-if="hasMore && stationsAll.length > 0">
          <text>{{ loadingMore ? '加载中...' : '加载更多' }}</text>
        </view>
        <view class="load-more" v-else-if="!hasMore && stationsAll.length > 0">
          <text>已加载全部加油站</text>
        </view>
      </scroll-view>
    </view>

    <view class="safe-area"></view>

    <!-- 定位权限提示弹窗 -->
    <view class="permission-modal" v-if="showPermissionModal">
      <view class="permission-content">
        <view class="permission-header">
          <text class="permission-title">位置权限申请</text>
        </view>
        <view class="permission-body">
          <text class="permission-text">为了提供精准的附近加油站服务，需要获取您的位置信息</text>
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
// 腾讯地图API配置（与map.vue一致）
const TENCENT_MAP_KEY = '4DYBZ-7QXEC-CWM2S-AXAZR-YLVQF-C6BPY';
const TENCENT_MAP_BASE_URL = 'https://apis.map.qq.com';

export default {
  data() {
    return {
      searchKeyword: '',
      activeFilter: 'all',
      selectedBrand: '',
      availableFilters: [
        { type: 'all', name: '全部' },
        { type: 'nearby', name: '最近' },
        { type: 'brand', name: '品牌' }
      ],
      
      stationsAll: [],
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
      
      brandList: [],
      favoriteIds: [],
      showPermissionModal: false,
      searchTimer: null
    }
  },
  computed: {
    filteredStations() {
      let stations = [...this.stationsAll];
      
      if (this.searchKeyword && this.searchKeyword.trim()) {
        const keyword = this.searchKeyword.trim().toLowerCase();
        stations = stations.filter(station => 
          station.name.toLowerCase().includes(keyword) || 
          station.address.toLowerCase().includes(keyword)
        );
      }
      
      if (this.activeFilter === 'nearby') {
        stations.sort((a, b) => (a.distanceValue || 0) - (b.distanceValue || 0));
      } else if (this.activeFilter === 'brand' && this.selectedBrand) {
        stations = stations.filter(station => station.brandName === this.selectedBrand);
        stations.sort((a, b) => (a.distanceValue || 0) - (b.distanceValue || 0));
      } else {
        stations.sort((a, b) => (a.distanceValue || 0) - (b.distanceValue || 0));
      }
      
      return stations;
    }
  },
  onLoad() {
    this.loadFavorites();
    this.getUserLocationAndLoadStations();
  },
  methods: {
    loadFavorites() {
      try {
        const favorites = uni.getStorageSync('gas_favorites');
        if (favorites && Array.isArray(favorites)) {
          this.favoriteIds = favorites;
        }
      } catch(e) {}
    },
    
    saveFavorites() {
      try {
        uni.setStorageSync('gas_favorites', this.favoriteIds);
      } catch(e) {}
    },
    
    getUserLocationAndLoadStations() {
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
          // 提示用户配置 requiredPrivateInfos
          if (err.errMsg && err.errMsg.includes('requiredPrivateInfos')) {
            uni.showModal({
              title: '定位配置缺失',
              content: '请在 app.json 中添加 "requiredPrivateInfos": ["getLocation"] 字段，并重新编译。',
              showCancel: false
            });
          }
          // 尝试IP定位兜底
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
      this.stationsAll = [];
      this.currentPage = 1;
      this.hasMore = true;
      this.searchKeyword = '';
      this.selectedBrand = '';
      this.activeFilter = 'all';
      this.loadStations(true);   // 关键：调用正确的方法名
    },
    
    async loadStations(reset = false) {
      if (!this.currentLocation.latitude || !this.currentLocation.longitude) {
        console.warn('位置未获取');
        return;
      }
      
      if (reset) {
        this.currentPage = 1;
        this.hasMore = true;
        this.loading = true;
        this.stationsAll = [];
      } else {
        if (this.loadingMore || !this.hasMore) return;
        this.loadingMore = true;
      }
      
      const params = {
        key: TENCENT_MAP_KEY,
        boundary: `nearby(${this.currentLocation.latitude},${this.currentLocation.longitude},3000)`,
        keyword: this.searchKeyword ? this.searchKeyword : '加油站',
        page_size: this.pageSize,
        page_index: this.currentPage,
        order_by: '_distance'
      };
      
      try {
        const res = await this.requestAPI(`${TENCENT_MAP_BASE_URL}/ws/place/v1/search`, params);
        if (res.status === 0 && res.data && res.data.length) {
          const newStations = this.parseStationsFromAPI(res.data);
          if (reset) {
            this.stationsAll = newStations;
          } else {
            this.stationsAll = [...this.stationsAll, ...newStations];
          }
          this.updateBrandList();
          
          const total = res.count || 0;
          const loadedCount = this.currentPage * this.pageSize;
          this.hasMore = loadedCount < total && newStations.length === this.pageSize;
          if (this.hasMore) {
            this.currentPage++;
          }
        } else {
          if (this.currentPage === 1) {
            uni.showToast({
              title: '未找到附近加油站',
              icon: 'none'
            });
          }
          this.hasMore = false;
        }
      } catch (error) {
        console.error('请求加油站数据失败:', error);
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
    
    parseStationsFromAPI(data) {
      return data.map((poi, index) => {
        let brandName = '其他';
        const title = poi.title || '';
        if (title.includes('中国石化') || title.includes('中石化')) brandName = '中国石化';
        else if (title.includes('中国石油') || title.includes('中石油')) brandName = '中国石油';
        else if (title.includes('壳牌')) brandName = '壳牌';
        else if (title.includes('BP') || title.includes('碧辟')) brandName = 'BP';
        else if (title.includes('中海油')) brandName = '中海油';
        
        let is24h = false;
        let openingStatus = '营业中';
        if (poi.opening_hours) {
          const hours = poi.opening_hours;
          if (hours.includes('24小时') || hours.includes('00:00-24:00') || hours.includes('0:00-24:00')) {
            is24h = true;
            openingStatus = '24小时';
          } else {
            openingStatus = hours.length > 20 ? hours.substring(0, 20) + '...' : hours;
          }
        }
        
        let hasDiscount = false;
        if (poi.category && (poi.category.includes('优惠') || poi.category.includes('折扣'))) {
          hasDiscount = true;
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
          id: poi.id || `temp_${Date.now()}_${index}`,
          name: poi.title || '加油站',
          address: poi.address || poi.location?.address || '地址信息待补充',
          distance: distance,
          distanceValue: distanceValue,
          phone: poi.tel || '',
          latitude: poi.location?.lat || 0,
          longitude: poi.location?.lng || 0,
          is24h: is24h,
          hasDiscount: hasDiscount,
          openingStatus: openingStatus,
          brandName: brandName,
          isFavorite: this.favoriteIds.includes(poi.id),
          rawPoi: poi
        };
      });
    },
    
    updateBrandList() {
      const brands = new Set();
      this.stationsAll.forEach(station => {
        if (station.brandName) brands.add(station.brandName);
      });
      this.brandList = Array.from(brands).sort();
    },
    
    onSearchInput() {
      if (this.searchTimer) clearTimeout(this.searchTimer);
      this.searchTimer = setTimeout(() => {
        if (this.searchKeyword.trim()) {
          this.resetAndLoad();
        } else {
          this.resetAndLoad();
        }
      }, 500);
    },
    
    onSearchCancel() {
      this.searchKeyword = '';
      this.resetAndLoad();
    },
    
    onFilterChange(filter) {
      if (filter.type === 'brand') {
        if (this.brandList.length === 0) {
          uni.showToast({
            title: '暂未获取到品牌信息',
            icon: 'none'
          });
          return;
        }
        uni.showActionSheet({
          itemList: this.brandList,
          success: (res) => {
            const selectedBrandName = this.brandList[res.tapIndex];
            this.selectedBrand = selectedBrandName;
            this.activeFilter = 'brand';
          },
          fail: () => {}
        });
      } else {
        this.selectedBrand = '';
        this.activeFilter = filter.type;
      }
    },
    
    clearBrandFilter() {
      this.selectedBrand = '';
      this.activeFilter = 'all';
    },
    
    loadMore() {
      if (!this.hasMore || this.loadingMore || this.loading) return;
      this.loadStations(false);
    },
    
    onRefresh() {
      this.refreshing = true;
      this.resetAndLoad();
    },
    
    viewStationDetail(station) {
      uni.navigateTo({
        url: `/pages/gas-station/detail?id=${station.id}&name=${encodeURIComponent(station.name)}&lat=${station.latitude}&lng=${station.longitude}`
      });
    },
    
    navigateToStation(station) {
      if (station.latitude && station.longitude) {
        uni.openLocation({
          latitude: station.latitude,
          longitude: station.longitude,
          name: station.name,
          address: station.address
        });
      } else {
        uni.showToast({
          title: '坐标信息缺失',
          icon: 'none'
        });
      }
    },
    
    callStation(station) {
      if (station.phone) {
        uni.makePhoneCall({
          phoneNumber: station.phone
        });
      } else {
        uni.showToast({
          title: '暂无联系电话',
          icon: 'none'
        });
      }
    },
    
    toggleFavorite(station) {
      const index = this.favoriteIds.indexOf(station.id);
      if (index === -1) {
        this.favoriteIds.push(station.id);
        station.isFavorite = true;
        uni.showToast({
          title: '已收藏',
          icon: 'success'
        });
      } else {
        this.favoriteIds.splice(index, 1);
        station.isFavorite = false;
        uni.showToast({
          title: '已取消收藏',
          icon: 'success'
        });
      }
      this.saveFavorites();
      const target = this.stationsAll.find(s => s.id === station.id);
      if (target) target.isFavorite = station.isFavorite;
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
              this.getUserLocationAndLoadStations();
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
/* 样式与之前相同，此处省略（保持原有样式） */
.gas-station-page {
  height: 100vh;
  background-color: #f8f8f8;
  display: flex;
  flex-direction: column;
}
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
.content-section {
  flex: 1;
  overflow: hidden;
}
.station-list {
  height: 100%;
  padding: 20rpx 30rpx;
}
.station-item {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 15rpx rgba(0, 0, 0, 0.06);
}
.station-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20rpx;
}
.station-name {
  font-size: 30rpx;
  color: #333;
  font-weight: 600;
  flex: 1;
  margin-right: 20rpx;
}
.station-tags {
  display: flex;
  gap: 10rpx;
  flex-wrap: wrap;
}
.station-tag {
  font-size: 20rpx;
  color: #ff6b6b;
  background: #ffeaea;
  padding: 6rpx 12rpx;
  border-radius: 12rpx;
  border: 1rpx solid #ffd6d6;
}
.station-tag.discount-tag {
  background: #fff0e0;
  color: #ff9a3c;
  border-color: #ffe0c0;
}
.station-tag.brand-tag {
  background: #e8f1ff;
  color: #5c9eff;
  border-color: #d4e4ff;
}
.station-info {
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
.price-section {
  display: flex;
  justify-content: space-between;
  background: #f8fbff;
  border-radius: 16rpx;
  padding: 20rpx;
  margin-bottom: 25rpx;
  border: 1rpx solid #e8f1ff;
}
.price-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}
.fuel-type {
  font-size: 22rpx;
  color: #999;
  margin-bottom: 8rpx;
}
.price {
  font-size: 24rpx;
  color: #333;
  font-weight: 500;
}
.station-actions {
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
.action-btn.navigation {
  background: #e8f1ff;
  color: #b8d4ff;
}
.action-btn.call {
  background: #f0f8f0;
  color: #6bcf7f;
}
.action-btn.favorite {
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