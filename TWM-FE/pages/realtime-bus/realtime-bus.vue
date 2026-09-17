<template>
  <view class="realtime-bus-page">
    <!-- 搜索栏 -->
    <view class="search-section">
      <view class="search-bar">
        <image class="search-icon" src="/static/icons/general/search.png" mode="aspectFit"></image>
        <input 
          class="search-input" 
          placeholder="搜索公交线路" 
          v-model="searchKeyword"
          @input="onSearchInput"
        />
        <view class="search-cancel" @tap="onSearchCancel" v-if="searchKeyword">
          <image class="cancel-icon" src="/static/icons/general/close.png" mode="aspectFit"></image>
        </view>
      </view>
    </view>

    <!-- 快速线路（常用线路） -->
    <view class="quick-lines-section" v-if="quickLines.length">
      <view class="section-header">
        <text class="section-title">常用线路</text>
        <view class="refresh-btn" @tap="refreshAllData">
          <image class="refresh-icon" src="/static/icons/general/refresh.png" mode="aspectFit"></image>
          <text>刷新</text>
        </view>
      </view>
      
      <scroll-view class="quick-lines-scroll" scroll-x :show-scrollbar="false">
        <view 
          class="quick-line-item" 
          v-for="line in quickLines" 
          :key="line.id"
          @tap="viewLineDetail(line)"
        >
          <view class="line-badge" :class="line.status">{{ line.statusText }}</view>
          <text class="line-number">{{ line.number }}</text>
          <text class="line-name">{{ line.name }}</text>
          <view class="line-realtime">
            <text class="realtime-text">{{ line.realtimeInfo }}</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 附近站点 -->
    <view class="nearby-stations-section">
      <view class="section-header">
        <text class="section-title">附近公交站</text>
        <view class="location-btn" @tap="locateMe">
          <image class="location-icon" src="/static/icons/general/location.png" mode="aspectFit"></image>
          <text>定位</text>
        </view>
      </view>
      
      <scroll-view class="stations-list" scroll-y :refresher-enabled="true" @refresherrefresh="refreshNearbyStations" :refresher-triggered="refreshing">
        <view v-if="loadingStations" class="loading-container">
          <text class="loading-text">正在获取附近公交站...</text>
        </view>
        <view v-else-if="nearbyStations.length === 0" class="empty-container">
          <text class="empty-text">未找到附近公交站</text>
        </view>
        <view 
          class="station-item" 
          v-for="station in nearbyStations" 
          :key="station.id"
        >
          <view class="station-header">
            <view class="station-name-wrap">
              <text class="station-name">{{ station.name }}</text>
              <text class="station-distance">{{ station.distance }}</text>
            </view>
            <view class="nav-btn" @tap.stop="navigateToStation(station)">
              <image class="nav-icon" src="/static/icons/general/navigation.png" mode="aspectFit"></image>
              <text>导航</text>
            </view>
          </view>
          
          <view class="station-lines">
            <view 
              class="line-item" 
              v-for="line in station.lines" 
              :key="line.id"
              @tap.stop="viewLineRealtime(line, station)"
            >
              <view class="line-info">
                <text class="line-number">{{ line.name }}</text>
                <text class="line-destination">{{ line.fromTo || '方向待更新' }}</text>
              </view>
              
              <view class="realtime-buses">
                <!-- 显示最近的一辆车 -->
                <view class="bus-item" v-if="line.buses && line.buses.length">
                  <text class="bus-distance">还有{{ line.buses[0].distance }}</text>
                  <text class="bus-time">约{{ line.buses[0].time }}</text>
                </view>
                <text class="no-bus" v-else>暂无车辆</text>
              </view>
            </view>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 线路搜索面板 -->
    <view class="line-search-panel" v-if="showLineSearch">
      <view class="search-header">
        <text class="search-title">搜索线路</text>
        <view class="search-close" @tap="hideLineSearch">
          <image class="close-icon" src="/static/icons/general/close.png" mode="aspectFit"></image>
        </view>
      </view>
      
      <view class="search-content">
        <view class="search-input-group">
          <input class="search-input" placeholder="请输入公交线路号" v-model="lineSearchKeyword" />
          <view class="search-action" @tap="searchLine">
            <text>搜索</text>
          </view>
        </view>
        
        <view class="search-results" v-if="lineSearchResults.length > 0">
          <view 
            class="result-item" 
            v-for="result in lineSearchResults" 
            :key="result.id"
            @tap="selectLineResult(result)"
          >
            <text class="result-number">{{ result.name }}</text>
            <text class="result-name">{{ result.title }}</text>
            <text class="result-status" :class="result.status">{{ result.statusText }}</text>
          </view>
        </view>
        
        <view class="search-history" v-else>
          <view class="history-header">
            <text class="history-title">搜索历史</text>
            <view class="clear-history" @tap="clearSearchHistory">
              <text>清空</text>
            </view>
          </view>
          <view class="history-list">
            <view 
              class="history-item" 
              v-for="item in searchHistory" 
              :key="item.id"
              @tap="selectHistoryItem(item)"
            >
              <text class="history-number">{{ item.number }}</text>
              <text class="history-name">{{ item.name }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 底部操作栏 -->
    <view class="bottom-actions">
      <view class="action-item" @tap="showLineSearch = true">
        <image class="action-icon" src="/static/icons/bus/search-line.png" mode="aspectFit"></image>
        <text>搜索线路</text>
      </view>
      <view class="action-item" @tap="viewNearbyMap">
        <image class="action-icon" src="/static/icons/general/map.png" mode="aspectFit"></image>
        <text>附近地图</text>
      </view>
      <view class="action-item" @tap="viewFavorites">
        <image class="action-icon" src="/static/icons/general/star.png" mode="aspectFit"></image>
        <text>我的收藏</text>
      </view>
    </view>

    <view class="safe-area"></view>

    <!-- 定位权限提示 -->
    <view class="permission-modal" v-if="showPermissionModal">
      <view class="permission-content">
        <view class="permission-header">
          <text class="permission-title">位置权限申请</text>
        </view>
        <view class="permission-body">
          <text class="permission-text">为了提供精准的附近公交站服务，需要获取您的位置信息</text>
        </view>
        <view class="permission-actions">
          <view class="permission-btn cancel" @tap="showPermissionModal = false">取消</view>
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
      showLineSearch: false,
      lineSearchKeyword: '',
      quickLines: [],        // 常用线路
      nearbyStations: [],    // 附近公交站
      loadingStations: false,
      refreshing: false,
      currentLocation: { latitude: null, longitude: null },
      showPermissionModal: false,
      searchTimer: null,
      lineSearchResults: [],
      searchHistory: [],
      favorites: []
    }
  },
  onLoad() {
    this.loadFavoritesAndHistory();
    this.getUserLocationAndLoadStations();
  },
  onPullDownRefresh() {
    this.refreshAllData();
  },
  methods: {
    // 加载收藏和历史
    loadFavoritesAndHistory() {
      try {
        const fav = uni.getStorageSync('bus_favorites') || [];
        this.favorites = fav;
        const hist = uni.getStorageSync('bus_search_history') || [];
        this.searchHistory = hist.slice(0, 10);
        if (this.favorites.length) {
          this.loadQuickLines(this.favorites.slice(0, 5));
        }
      } catch(e) {}
    },
    saveFavorites() {
      uni.setStorageSync('bus_favorites', this.favorites);
    },
    saveSearchHistory() {
      uni.setStorageSync('bus_search_history', this.searchHistory.slice(0, 10));
    },
    async loadQuickLines(lineIds) {
      const quick = [];
      for (let id of lineIds) {
        const found = this.searchHistory.find(h => h.id === id);
        if (found) {
          quick.push({
            id: found.id,
            number: found.number,
            name: found.name,
            status: 'normal',
            statusText: '正常',
            realtimeInfo: '获取中...'
          });
        }
      }
      this.quickLines = quick;
      for (let line of this.quickLines) {
        this.fetchLineRealtimeInfo(line);
      }
    },
    async fetchLineRealtimeInfo(line) {
      if (!line.lineUid) return;
      try {
        const res = await this.requestAPI(`${TENCENT_MAP_BASE_URL}/ws/bus/v1/realtime`, {
          key: TENCENT_MAP_KEY,
          line_uid: line.lineUid,
          output: 'json'
        });
        if (res.status === 0 && res.result) {
          const vehicles = res.result.vehicles || [];
          line.realtimeInfo = vehicles.length ? `${vehicles.length}辆车在运行` : '暂无车辆';
          if (vehicles.length > 10) line.status = 'crowded', line.statusText = '拥挤';
          else if (vehicles.length > 5) line.status = 'normal', line.statusText = '正常';
          else line.status = 'slow', line.statusText = '缓行';
        }
      } catch(e) {}
    },
    getUserLocationAndLoadStations() {
      this.loadingStations = true;
      uni.getLocation({
        type: 'gcj02',
        success: (res) => {
          this.currentLocation.latitude = res.latitude;
          this.currentLocation.longitude = res.longitude;
          this.loadNearbyStations();
        },
        fail: (err) => {
          console.error('定位失败', err);
          this.tryTencentIPLocation();
        }
      });
    },
    async tryTencentIPLocation() {
      try {
        const res = await this.requestAPI(`${TENCENT_MAP_BASE_URL}/ws/location/v1/ip`, { key: TENCENT_MAP_KEY, output: 'json' });
        if (res.status === 0 && res.result && res.result.location) {
          this.currentLocation.latitude = res.result.location.lat;
          this.currentLocation.longitude = res.result.location.lng;
          uni.showToast({ title: '使用IP定位', icon: 'none', duration: 1500 });
          this.loadNearbyStations();
        } else throw new Error('IP定位失败');
      } catch (e) {
        console.error('IP定位失败', e);
        this.loadingStations = false;
        this.showPermissionModal = true;
      }
    },
    async loadNearbyStations() {
      if (!this.currentLocation.latitude || !this.currentLocation.longitude) return;
      this.loadingStations = true;
      try {
        const params = {
          key: TENCENT_MAP_KEY,
          boundary: `nearby(${this.currentLocation.latitude},${this.currentLocation.longitude},1500)`,
          keyword: '公交站',
          page_size: 20,
          order_by: '_distance'
        };
        const res = await this.requestAPI(`${TENCENT_MAP_BASE_URL}/ws/place/v1/search`, params);
        if (res.status === 0 && res.data && res.data.length) {
          const stations = [];
          for (let poi of res.data.slice(0, 15)) {
            const station = {
              id: poi.id,
              name: poi.title,
              address: poi.address,
              distance: poi._distance < 1000 ? `${Math.round(poi._distance)}m` : `${(poi._distance / 1000).toFixed(1)}km`,
              distanceValue: poi._distance,
              latitude: poi.location.lat,
              longitude: poi.location.lng,
              lines: []
            };
            stations.push(station);
          }
          this.nearbyStations = stations;
          await this.fetchStationsLines(stations.slice(0, 8));
          await this.fetchAllLinesRealtime();
        } else {
          this.nearbyStations = [];
        }
      } catch (err) {
        console.error('加载附近公交站失败', err);
        uni.showToast({ title: '获取公交站失败', icon: 'none' });
      } finally {
        this.loadingStations = false;
        this.refreshing = false;
        uni.stopPullDownRefresh();
      }
    },
    async fetchStationsLines(stations) {
      for (let station of stations) {
        try {
          const detailRes = await this.requestAPI(`${TENCENT_MAP_BASE_URL}/ws/place/v1/detail`, {
            key: TENCENT_MAP_KEY,
            id: station.id,
            output: 'json'
          });
          if (detailRes.status === 0 && detailRes.result && detailRes.result.poi) {
            const busLines = detailRes.result.poi.bus || [];
            station.lines = busLines.map(line => ({
              id: line.id,
              name: line.name,
              fromTo: line.from_to || '',
              lineUid: line.line_uid,
              stopId: line.stop_id,
              buses: []
            }));
          } else {
            station.lines = [];
          }
        } catch (e) {
          console.warn(`获取站点${station.name}线路失败`, e);
          station.lines = [];
        }
      }
    },
    async fetchAllLinesRealtime() {
      const allLines = [];
      this.nearbyStations.forEach(station => {
        station.lines.forEach(line => {
          if (line.lineUid && line.stopId) {
            allLines.push({ station, line });
          }
        });
      });
      const chunkSize = 5;
      for (let i = 0; i < allLines.length; i += chunkSize) {
        const chunk = allLines.slice(i, i + chunkSize);
        await Promise.all(chunk.map(item => this.fetchLineRealtimeForStop(item.station, item.line)));
      }
    },
    async fetchLineRealtimeForStop(station, line) {
      if (!line.lineUid || !line.stopId) return;
      try {
        const res = await this.requestAPI(`${TENCENT_MAP_BASE_URL}/ws/bus/v1/realtime`, {
          key: TENCENT_MAP_KEY,
          line_uid: line.lineUid,
          stop_uid: line.stopId,
          output: 'json'
        });
        if (res.status === 0 && res.result) {
          const vehicles = res.result.vehicles || [];
          line.buses = vehicles.map((v, idx) => {
            let distanceText = '';
            let timeText = '';
            if (v.distance !== undefined) {
              const stationsAway = Math.ceil(v.distance / 1000); // 粗略估算站数（假设站距1km）
              distanceText = `${stationsAway}站`;
            } else {
              distanceText = '未知';
            }
            if (v.duration !== undefined) {
              timeText = `${v.duration}分钟`;
            } else {
              timeText = '即将到站';
            }
            return {
              id: v.vehicle_id || idx,
              distance: distanceText,
              time: timeText,
              status: v.duration <= 2 ? 'arriving' : 'normal'
            };
          });
          if (line.buses.length === 0) {
            line.buses = [];
          }
        } else {
          line.buses = [];
        }
      } catch (e) {
        console.warn(`获取线路${line.name}实时信息失败`, e);
        line.buses = [];
      }
    },
    async refreshAllData() {
      this.refreshing = true;
      await this.loadNearbyStations();
      if (this.favorites.length) {
        await this.loadQuickLines(this.favorites.slice(0, 5));
      }
    },
    refreshNearbyStations() {
      this.refreshAllData();
    },
    onSearchInput() {
      if (this.searchTimer) clearTimeout(this.searchTimer);
      this.searchTimer = setTimeout(() => {
        if (this.searchKeyword.trim()) {
          this.searchStationsByKeyword(this.searchKeyword);
        } else {
          this.loadNearbyStations();
        }
      }, 500);
    },
    async searchStationsByKeyword(keyword) {
      if (!this.currentLocation.latitude) return;
      this.loadingStations = true;
      try {
        const params = {
          key: TENCENT_MAP_KEY,
          keyword: keyword,
          boundary: `nearby(${this.currentLocation.latitude},${this.currentLocation.longitude},5000)`,
          page_size: 20,
          order_by: '_distance'
        };
        const res = await this.requestAPI(`${TENCENT_MAP_BASE_URL}/ws/place/v1/search`, params);
        if (res.status === 0 && res.data.length) {
          const stations = res.data.map(poi => ({
            id: poi.id,
            name: poi.title,
            address: poi.address,
            distance: poi._distance < 1000 ? `${Math.round(poi._distance)}m` : `${(poi._distance / 1000).toFixed(1)}km`,
            distanceValue: poi._distance,
            latitude: poi.location.lat,
            longitude: poi.location.lng,
            lines: []
          }));
          this.nearbyStations = stations.slice(0, 15);
          await this.fetchStationsLines(this.nearbyStations.slice(0, 8));
          await this.fetchAllLinesRealtime();
        } else {
          this.nearbyStations = [];
          uni.showToast({ title: '未找到相关公交站', icon: 'none' });
        }
      } catch (err) {
        console.error('搜索失败', err);
      } finally {
        this.loadingStations = false;
      }
    },
    onSearchCancel() {
      this.searchKeyword = '';
      this.loadNearbyStations();
    },
    async searchLine() {
      if (!this.lineSearchKeyword.trim()) {
        uni.showToast({ title: '请输入线路号', icon: 'none' });
        return;
      }
      uni.showLoading({ title: '搜索中...' });
      try {
        const params = {
          key: TENCENT_MAP_KEY,
          keyword: this.lineSearchKeyword,
          city: this.currentLocation.city || '',
          output: 'json'
        };
        const res = await this.requestAPI(`${TENCENT_MAP_BASE_URL}/ws/bus/v1/search`, params);
        uni.hideLoading();
        if (res.status === 0 && res.result && res.result.lines && res.result.lines.length) {
          this.lineSearchResults = res.result.lines.map(line => ({
            id: line.uid,
            name: line.name,
            title: line.title || line.name,
            fromTo: line.from + ' - ' + line.to,
            lineUid: line.uid,
            status: 'normal',
            statusText: '正常'
          }));
          const historyItem = {
            id: res.result.lines[0].uid,
            number: this.lineSearchKeyword,
            name: res.result.lines[0].name
          };
          this.addToSearchHistory(historyItem);
        } else {
          this.lineSearchResults = [];
          uni.showToast({ title: '未找到该线路', icon: 'none' });
        }
      } catch (err) {
        uni.hideLoading();
        uni.showToast({ title: '搜索失败', icon: 'none' });
      }
    },
    addToSearchHistory(item) {
      const exists = this.searchHistory.some(h => h.id === item.id);
      if (!exists) {
        this.searchHistory.unshift(item);
        if (this.searchHistory.length > 10) this.searchHistory = this.searchHistory.slice(0, 10);
        this.saveSearchHistory();
      }
    },
    selectLineResult(result) {
      this.hideLineSearch();
      this.viewLineDetail(result);
    },
    selectHistoryItem(item) {
      this.lineSearchKeyword = item.number;
      this.searchLine();
    },
    clearSearchHistory() {
      uni.showModal({
        title: '清空历史',
        content: '确定要清空搜索历史吗？',
        success: (res) => {
          if (res.confirm) {
            this.searchHistory = [];
            this.saveSearchHistory();
            uni.showToast({ title: '已清空', icon: 'success' });
          }
        }
      });
    },
    viewLineDetail(line) {
      uni.navigateTo({ url: `/pages/bus/line-detail?id=${line.id}&number=${line.name}` });
    },
    viewStationDetail(station) {
      uni.navigateTo({ url: `/pages/bus/station-detail?id=${station.id}&name=${encodeURIComponent(station.name)}&lat=${station.latitude}&lng=${station.longitude}` });
    },
    viewLineRealtime(line, station) {
      uni.navigateTo({ url: `/pages/bus/line-realtime?lineId=${line.id}&stationId=${station.id}&lineName=${encodeURIComponent(line.name)}` });
    },
    // 导航到公交站
    navigateToStation(station) {
      if (station.latitude && station.longitude) {
        uni.openLocation({
          latitude: station.latitude,
          longitude: station.longitude,
          name: station.name,
          address: station.address
        });
      } else {
        uni.showToast({ title: '坐标信息缺失', icon: 'none' });
      }
    },
    locateMe() {
      this.getUserLocationAndLoadStations();
    },
    hideLineSearch() {
      this.showLineSearch = false;
      this.lineSearchKeyword = '';
      this.lineSearchResults = [];
    },
    viewNearbyMap() {
      if (this.currentLocation.latitude) {
        uni.openLocation({
          latitude: this.currentLocation.latitude,
          longitude: this.currentLocation.longitude,
          name: '当前位置'
        });
      } else {
        uni.getLocation({
          success: (res) => {
            uni.openLocation({
              latitude: res.latitude,
              longitude: res.longitude
            });
          },
          fail: () => uni.showToast({ title: '定位失败', icon: 'none' })
        });
      }
    },
    viewFavorites() {
      uni.navigateTo({ url: '/pages/bus/favorites' });
    },
    requestLocationPermission() {
      this.showPermissionModal = false;
      uni.openSetting({
        success: (res) => {
          if (res.authSetting['scope.userLocation']) this.getUserLocationAndLoadStations();
        }
      });
    },
    requestAPI(url, params) {
      return new Promise((resolve, reject) => {
        uni.request({
          url: url,
          method: 'GET',
          data: params,
          timeout: 15000,
          success: (res) => {
            if (res.statusCode === 200 && res.data.status === 0) resolve(res.data);
            else reject(new Error(res.data.message || '请求失败'));
          },
          fail: reject
        });
      });
    }
  }
}
</script>

<style scoped>
.realtime-bus-page {
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

.quick-lines-section {
  background: #fff;
  padding: 30rpx;
  border-bottom: 1rpx solid #eee;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25rpx;
}

.section-title {
  font-size: 32rpx;
  color: #333;
  font-weight: 600;
}

.refresh-btn, .location-btn {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 26rpx;
  color: #b8d4ff;
}

.refresh-icon, .location-icon {
  width: 24rpx;
  height: 24rpx;
}

.quick-lines-scroll {
  white-space: nowrap;
}

.quick-line-item {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  background: #f8f8f8;
  border-radius: 20rpx;
  padding: 25rpx 20rpx;
  margin-right: 20rpx;
  min-width: 180rpx;
  position: relative;
  transition: all 0.3s ease;
}

.quick-line-item:active {
  background: #e8f1ff;
  transform: scale(0.98);
}

.line-badge {
  position: absolute;
  top: 15rpx;
  right: 15rpx;
  font-size: 20rpx;
  padding: 4rpx 8rpx;
  border-radius: 8rpx;
  color: #fff;
}

.line-badge.normal { background: #6bcf7f; }
.line-badge.crowded { background: #ff6b6b; }
.line-badge.slow { background: #ffb400; }

.line-number {
  font-size: 36rpx;
  color: #b8d4ff;
  font-weight: 600;
  margin-bottom: 10rpx;
}

.line-name {
  font-size: 22rpx;
  color: #666;
  text-align: center;
  margin-bottom: 15rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 100%;
}

.line-realtime {
  font-size: 20rpx;
  color: #999;
}

.nearby-stations-section {
  flex: 1;
  background: #fff;
  padding: 30rpx;
  overflow: hidden;
}

.stations-list {
  height: 100%;
}

.station-item {
  background: #f8f8f8;
  border-radius: 20rpx;
  padding: 25rpx;
  margin-bottom: 20rpx;
}

.station-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
  padding-bottom: 15rpx;
  border-bottom: 1rpx solid #eee;
}

.station-name-wrap {
  display: flex;
  align-items: baseline;
  gap: 15rpx;
  flex-wrap: wrap;
}

.station-name {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
}

.station-distance {
  font-size: 24rpx;
  color: #999;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 6rpx;
  background: #e8f1ff;
  padding: 10rpx 20rpx;
  border-radius: 30rpx;
  font-size: 24rpx;
  color: #b8d4ff;
}

.nav-icon {
  width: 28rpx;
  height: 28rpx;
}

.station-lines {
  display: flex;
  flex-direction: column;
  gap: 15rpx;
}

.line-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15rpx;
  background: #fff;
  border-radius: 12rpx;
  transition: all 0.3s ease;
}

.line-item:active {
  background: #f0f7ff;
}

.line-info {
  display: flex;
  align-items: center;
  gap: 15rpx;
  flex: 1;
}

.line-number {
  font-size: 26rpx;
  color: #b8d4ff;
  font-weight: 600;
  min-width: 80rpx;
}

.line-destination {
  font-size: 24rpx;
  color: #666;
  flex: 1;
}

.realtime-buses {
  display: flex;
  gap: 10rpx;
}

.bus-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8rpx 12rpx;
  border-radius: 8rpx;
  min-width: 100rpx;
  background: #f0f7ff;
  color: #b8d4ff;
}

.bus-distance {
  font-size: 20rpx;
  font-weight: 500;
  margin-bottom: 4rpx;
}

.bus-time {
  font-size: 18rpx;
  opacity: 0.8;
}

.no-bus {
  font-size: 22rpx;
  color: #999;
  padding: 8rpx 12rpx;
}

.line-search-panel {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  flex-direction: column;
}

.search-header {
  background: #fff;
  padding: 30rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1rpx solid #eee;
}

.search-title {
  font-size: 32rpx;
  color: #333;
  font-weight: 600;
}

.search-close {
  width: 40rpx;
  height: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-icon {
  width: 24rpx;
  height: 24rpx;
}

.search-content {
  flex: 1;
  background: #fff;
  padding: 30rpx;
}

.search-input-group {
  display: flex;
  gap: 15rpx;
  margin-bottom: 30rpx;
}

.search-input-group .search-input {
  flex: 1;
  background: #f5f5f5;
  border-radius: 12rpx;
  padding: 20rpx;
  font-size: 28rpx;
  color: #333;
}

.search-action {
  background: #b8d4ff;
  color: #fff;
  padding: 20rpx 30rpx;
  border-radius: 12rpx;
  font-size: 28rpx;
  font-weight: 500;
}

.search-results {
  margin-bottom: 30rpx;
}

.result-item {
  display: flex;
  align-items: center;
  padding: 25rpx;
  background: #f8f8f8;
  border-radius: 12rpx;
  margin-bottom: 15rpx;
  transition: all 0.3s ease;
}

.result-item:active {
  background: #e8f1ff;
}

.result-number {
  font-size: 28rpx;
  color: #b8d4ff;
  font-weight: 600;
  min-width: 100rpx;
}

.result-name {
  font-size: 26rpx;
  color: #333;
  flex: 1;
  margin: 0 15rpx;
}

.result-status {
  font-size: 22rpx;
  padding: 6rpx 12rpx;
  border-radius: 8rpx;
  color: #fff;
}

.result-status.normal { background: #6bcf7f; }

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.history-title {
  font-size: 26rpx;
  color: #333;
  font-weight: 500;
}

.clear-history {
  font-size: 24rpx;
  color: #999;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 15rpx;
}

.history-item {
  display: flex;
  align-items: center;
  padding: 20rpx;
  background: #f8f8f8;
  border-radius: 12rpx;
  transition: all 0.3s ease;
}

.history-item:active {
  background: #e8f1ff;
}

.history-number {
  font-size: 26rpx;
  color: #b8d4ff;
  font-weight: 600;
  min-width: 100rpx;
}

.history-name {
  font-size: 26rpx;
  color: #666;
  flex: 1;
}

.bottom-actions {
  background: #fff;
  border-top: 1rpx solid #eee;
  display: flex;
  justify-content: space-around;
  padding: 20rpx 0;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  transition: all 0.3s ease;
}

.action-item:active {
  transform: scale(0.95);
}

.action-icon {
  width: 40rpx;
  height: 40rpx;
}

.action-item text {
  font-size: 22rpx;
  color: #666;
}

.safe-area {
  height: env(safe-area-inset-bottom);
  background: #fff;
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
}

.permission-btn.cancel {
  color: #999;
  border-right: 1rpx solid #eee;
}

.permission-btn.confirm {
  color: #b8d4ff;
  font-weight: 500;
}
</style>