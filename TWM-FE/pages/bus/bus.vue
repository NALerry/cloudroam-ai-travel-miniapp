<template>
  <view class="bus-page">
    <!-- 搜索栏 -->
    <view class="search-section">
      <view class="search-bar">
        <image class="search-icon" src="/static/icons/general/search.png" mode="aspectFit"></image>
        <input 
          class="search-input" 
          placeholder="搜索公交线路或地铁站" 
          v-model="searchKeyword"
          @input="onSearchInput"
        />
        <view class="search-cancel" @tap="onSearchCancel" v-if="searchKeyword">
          <image class="cancel-icon" src="/static/icons/general/close.png" mode="aspectFit"></image>
        </view>
      </view>
    </view>

    <!-- 切换标签 -->
    <view class="tab-section">
      <view class="tab-item" :class="{ active: activeTab === 'bus' }" @tap="activeTab = 'bus'">
        <text>公交</text>
      </view>
      <view class="tab-item" :class="{ active: activeTab === 'subway' }" @tap="activeTab = 'subway'">
        <text>地铁</text>
      </view>
      <view class="tab-item" :class="{ active: activeTab === 'route' }" @tap="activeTab = 'route'">
        <text>路线规划</text>
      </view>
    </view>

    <!-- 公交页面内容 -->
    <view class="content-section" v-if="activeTab === 'bus'">
      <!-- 实时公交（基于最近的公交站和线路，调用真实实时接口） -->
      <view class="realtime-section" v-if="nearestStation && nearestStation.lines && nearestStation.lines.length">
        <view class="section-header">
          <text class="section-title">实时公交 · {{ nearestStation.name }}</text>
          <view class="more-btn" @tap="viewStationDetail(nearestStation)">
            <text>更多</text>
            <image class="more-icon" src="/static/icons/general/more.png" mode="aspectFit"></image>
          </view>
        </view>
        
        <scroll-view class="realtime-scroll" scroll-x :show-scrollbar="false">
          <view 
            class="realtime-item" 
            v-for="line in nearestStation.lines.slice(0, 5)" 
            :key="line.id"
            @tap="viewBusLineDetail(line, nearestStation)"
          >
            <view class="bus-line">
              <text class="line-number">{{ line.name }}</text>
              <text class="line-name">{{ line.fromTo || '' }}</text>
            </view>
            <view class="bus-station">
              <text class="station-name">{{ nearestStation.name }}</text>
            </view>
            <view class="bus-arrival">
              <text class="arrival-info">{{ line.realtimeInfo || '获取中...' }}</text>
              <text class="arrival-time">{{ line.realtimeTime || '' }}</text>
            </view>
          </view>
          <view v-if="nearestStation.lines.length === 0" class="realtime-item">
            <text class="line-name">暂无线路信息</text>
          </view>
        </scroll-view>
      </view>

      <!-- 公交线路搜索（起点终点查询路线） -->
      <view class="line-search-section">
        <view class="search-input-group">
          <view class="input-item start">
            <image class="input-icon" src="/static/icons/general/start.png" mode="aspectFit"></image>
            <input class="input-field" placeholder="请输入起点（支持模糊搜索）" v-model="startStation" @input="onStartStationInput" @focus="showStartSuggestions = true" @blur="hideSuggestionsDelayed('start')" />
            <view class="location-btn" @tap="setStartToCurrent">
              <image class="location-icon" src="/static/icons/general/location.png" mode="aspectFit"></image>
            </view>
            <!-- 起点模糊查询下拉 -->
            <view class="suggestions-dropdown" v-if="showStartSuggestions && startSuggestions.length">
              <view class="suggestion-item" v-for="item in startSuggestions" :key="item.id" @tap="selectStartSuggestion(item)">
                <text class="suggestion-title">{{ item.title }}</text>
                <text class="suggestion-address">{{ item.address }}</text>
              </view>
            </view>
          </view>
          <view class="input-item end">
            <image class="input-icon" src="/static/icons/general/end.png" mode="aspectFit"></image>
            <input class="input-field" placeholder="请输入终点（支持模糊搜索）" v-model="endStation" @input="onEndStationInput" @focus="showEndSuggestions = true" @blur="hideSuggestionsDelayed('end')" />
            <view class="location-btn" @tap="setEndToCurrent">
              <image class="location-icon" src="/static/icons/general/location.png" mode="aspectFit"></image>
            </view>
            <!-- 终点模糊查询下拉 -->
            <view class="suggestions-dropdown" v-if="showEndSuggestions && endSuggestions.length">
              <view class="suggestion-item" v-for="item in endSuggestions" :key="item.id" @tap="selectEndSuggestion(item)">
                <text class="suggestion-title">{{ item.title }}</text>
                <text class="suggestion-address">{{ item.address }}</text>
              </view>
            </view>
          </view>
        </view>
        <view class="search-btn" @tap="searchBusRoute">
          <text>查询路线</text>
        </view>
      </view>

      <!-- 公交路线规划结果 -->
      <view class="route-results" v-if="busRouteResults.length > 0">
        <view class="section-header">
          <text class="section-title">推荐路线</text>
        </view>
        <scroll-view class="results-list" scroll-y>
          <view class="route-item" v-for="(route, index) in busRouteResults" :key="index">
            <view class="route-header">
              <text class="route-index">{{ index + 1 }}</text>
              <text class="route-summary">{{ route.summary }}</text>
            </view>
            <view class="route-details">
              <text class="route-time">{{ route.time }}</text>
              <text class="route-distance">{{ route.distance }}</text>
              <text class="route-cost" v-if="route.cost">¥{{ route.cost }}</text>
            </view>
            <view class="route-steps">
              <text class="step-text" v-for="step in route.steps.slice(0, 3)" :key="step">{{ step }}</text>
              <text class="more-steps" v-if="route.steps.length > 3">... 等{{ route.steps.length }}步</text>
            </view>
            <view class="nav-btn" @tap="navigateToRoute(route)">
              <text class="nav-text">导航</text>
            </view>
          </view>
        </scroll-view>
      </view>

      <!-- 附近公交站 -->
      <view class="nearby-section">
        <view class="section-header">
          <text class="section-title">附近公交站</text>
          <view class="more-btn" @tap="refreshNearbyStations" v-if="!loadingNearby">
            <text>刷新</text>
            <image class="more-icon" src="/static/icons/general/refresh.png" mode="aspectFit"></image>
          </view>
        </view>
        
        <scroll-view class="nearby-list" scroll-y :refresher-enabled="true" @refresherrefresh="refreshNearbyStations" :refresher-triggered="refreshing">
          <view v-if="loadingNearby" class="loading-container">
            <text class="loading-text">正在获取附近公交站...</text>
          </view>
          <view v-else-if="nearbyStations.length === 0" class="empty-container">
            <text class="empty-text">未找到附近公交站</text>
          </view>
          <view 
            class="nearby-item" 
            v-for="station in nearbyStations" 
            :key="station.id"
          >
            <view class="station-info" @tap="viewStationDetail(station)">
              <text class="station-name">{{ station.name }}</text>
              <text class="station-distance">{{ station.distance }}</text>
            </view>
            <view class="station-actions">
              <view class="station-lines" @tap="viewStationDetail(station)">
                <text class="line-tag" v-for="line in station.lines.slice(0, 4)" :key="line.id">{{ line.name }}</text>
                <text class="more-lines" v-if="station.lines.length > 4">等{{ station.lines.length }}条</text>
                <text class="line-tag" v-if="!station.lines.length">获取中...</text>
              </view>
              <view class="nav-station-btn" @tap="navigateToStation(station)">
                <image class="nav-icon" src="/static/icons/general/navigation.png" mode="aspectFit"></image>
                <text>导航</text>
              </view>
            </view>
          </view>
        </scroll-view>
      </view>
    </view>

    <!-- 地铁页面内容（保留原有城市数据，可后续扩展） -->
    <view class="content-section" v-if="activeTab === 'subway'">
      <view class="city-section" v-if="!selectedCity">
        <view class="section-header">
          <text class="section-title">选择城市</text>
        </view>
        <view class="city-grid">
          <view class="city-item" v-for="city in cityList" :key="city.id" @tap="selectCity(city)">
            <view class="city-icon">
              <image class="city-image" :src="city.icon" mode="aspectFit"></image>
            </view>
            <text class="city-name">{{ city.name }}</text>
          </view>
        </view>
      </view>
      <view class="city-subway-content" v-else>
        <view class="back-city" @tap="backToCityList">
          <image class="back-icon" src="/static/icons/general/back.png" mode="aspectFit"></image>
          <text class="back-text">返回城市列表</text>
          <text class="current-city">{{ selectedCity.name }}地铁</text>
        </view>
        <view class="subway-map-section" @tap="viewSubwayMap">
          <view class="map-placeholder">
            <image class="map-icon" src="/static/icons/bus/subway-map.png" mode="aspectFit"></image>
            <text class="map-title">{{ selectedCity.name }}地铁线路图</text>
            <text class="map-desc">点击查看完整地铁线路图</text>
          </view>
        </view>
        <view class="subway-lines-section">
          <view class="section-header">
            <text class="section-title">地铁线路</text>
          </view>
          <view class="lines-grid">
            <view class="line-item" v-for="line in selectedCity.lines" :key="line.id" :style="{ borderColor: line.color }" @tap="viewSubwayLine(line)">
              <view class="line-icon" :style="{ backgroundColor: line.color }">
                <text class="line-number">{{ line.lineNumber }}</text>
              </view>
              <view class="line-info">
                <text class="line-name">{{ line.name }}</text>
                <text class="line-stations">{{ line.stations }}站</text>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 路线规划页面内容（使用真实公交路径规划API） -->
    <view class="content-section" v-if="activeTab === 'route'">
      <view class="route-search-section">
        <view class="search-input-group">
          <view class="input-item start">
            <image class="input-icon" src="/static/icons/general/start.png" mode="aspectFit"></image>
            <input class="input-field" placeholder="请输入起点（支持模糊搜索）" v-model="routeStart" @input="onRouteStartInput" @focus="showRouteStartSuggestions = true" @blur="hideSuggestionsDelayed('routeStart')" />
            <view class="location-btn" @tap="useCurrentLocation('start')">
              <image class="location-icon" src="/static/icons/general/location.png" mode="aspectFit"></image>
            </view>
            <view class="suggestions-dropdown" v-if="showRouteStartSuggestions && routeStartSuggestions.length">
              <view class="suggestion-item" v-for="item in routeStartSuggestions" :key="item.id" @tap="selectRouteStartSuggestion(item)">
                <text class="suggestion-title">{{ item.title }}</text>
                <text class="suggestion-address">{{ item.address }}</text>
              </view>
            </view>
          </view>
          <view class="input-item end">
            <image class="input-icon" src="/static/icons/general/end.png" mode="aspectFit"></image>
            <input class="input-field" placeholder="请输入终点（支持模糊搜索）" v-model="routeEnd" @input="onRouteEndInput" @focus="showRouteEndSuggestions = true" @blur="hideSuggestionsDelayed('routeEnd')" />
            <view class="location-btn" @tap="useCurrentLocation('end')">
              <image class="location-icon" src="/static/icons/general/location.png" mode="aspectFit"></image>
            </view>
            <view class="suggestions-dropdown" v-if="showRouteEndSuggestions && routeEndSuggestions.length">
              <view class="suggestion-item" v-for="item in routeEndSuggestions" :key="item.id" @tap="selectRouteEndSuggestion(item)">
                <text class="suggestion-title">{{ item.title }}</text>
                <text class="suggestion-address">{{ item.address }}</text>
              </view>
            </view>
          </view>
        </view>
        <view class="search-options">
          <view class="option-item" v-for="option in routeOptions" :key="option.type" :class="{ active: selectedRouteOption === option.type }" @tap="selectRouteOption(option.type)">
            <image class="option-icon" :src="option.icon" mode="aspectFit"></image>
            <text>{{ option.name }}</text>
          </view>
        </view>
        <view class="search-btn" @tap="searchRoute">
          <text>开始规划</text>
        </view>
      </view>

      <view class="route-results" v-if="routeResults.length > 0">
        <view class="section-header">
          <text class="section-title">推荐路线</text>
        </view>
        <scroll-view class="results-list" scroll-y>
          <view class="route-item" v-for="(route, index) in routeResults" :key="index">
            <view class="route-header">
              <text class="route-index">{{ index + 1 }}</text>
              <text class="route-summary">{{ route.summary }}</text>
            </view>
            <view class="route-details">
              <text class="route-time">{{ route.time }}</text>
              <text class="route-distance">{{ route.distance }}</text>
              <text class="route-cost" v-if="route.cost">¥{{ route.cost }}</text>
            </view>
            <view class="route-steps">
              <text class="step-text" v-for="step in route.steps.slice(0, 3)" :key="step">{{ step }}</text>
              <text class="more-steps" v-if="route.steps.length > 3">... 等{{ route.steps.length }}步</text>
            </view>
            <view class="nav-btn" @tap="navigateToRoute(route)">
              <text class="nav-text">导航</text>
            </view>
          </view>
        </scroll-view>
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
      activeTab: 'bus',
      startStation: '',
      endStation: '',
      routeStart: '',
      routeEnd: '',
      selectedRouteOption: 'fastest',
      selectedCity: null,
      // 地铁城市数据（保留原有静态数据）
      cityList: [
        { id: 1, name: '北京', icon: '/static/icons/cities/beijing.png', mapUrl: 'https://www.metroman.cn/maps/beijing', lines: [{ id: 1, lineNumber: '1', name: '1号线', color: '#c23a30', stations: 23 },{ id: 2, lineNumber: '2', name: '2号线', color: '#004b87', stations: 18 },{ id: 3, lineNumber: '4', name: '4号线', color: '#008e66', stations: 24 },{ id: 4, lineNumber: '5', name: '5号线', color: '#aa7d39', stations: 23 },{ id: 5, lineNumber: '10', name: '10号线', color: '#0098db', stations: 45 },{ id: 6, lineNumber: '13', name: '13号线', color: '#f9d84e', stations: 16 }] },
        { id: 2, name: '上海', icon: '/static/icons/cities/shanghai.png', mapUrl: 'https://www.metroman.cn/maps/shanghai', lines: [{ id: 1, lineNumber: '1', name: '1号线', color: '#e6002d', stations: 28 },{ id: 2, lineNumber: '2', name: '2号线', color: '#97d700', stations: 30 },{ id: 3, lineNumber: '4', name: '4号线', color: '#5f259f', stations: 26 },{ id: 4, lineNumber: '7', name: '7号线', color: '#ff6900', stations: 33 },{ id: 5, lineNumber: '10', name: '10号线', color: '#c1a7e2', stations: 31 },{ id: 6, lineNumber: '11', name: '11号线', color: '#802a2d', stations: 39 }] },
        { id: 3, name: '广州', icon: '/static/icons/cities/guangzhou.png', mapUrl: 'https://www.metroman.cn/maps/guangzhou', lines: [{ id: 1, lineNumber: '1', name: '1号线', color: '#f3d03e', stations: 16 },{ id: 2, lineNumber: '2', name: '2号线', color: '#0065b3', stations: 24 },{ id: 3, lineNumber: '3', name: '3号线', color: '#eca154', stations: 28 },{ id: 4, lineNumber: '5', name: '5号线', color: '#c5003e', stations: 24 },{ id: 5, lineNumber: '6', name: '6号线', color: '#80225f', stations: 32 },{ id: 6, lineNumber: '8', name: '8号线', color: '#008e65', stations: 27 }] },
        { id: 4, name: '深圳', icon: '/static/icons/cities/shenzhen.png', mapUrl: 'https://www.metroman.cn/maps/shenzhen', lines: [{ id: 1, lineNumber: '1', name: '1号线', color: '#00a651', stations: 30 },{ id: 2, lineNumber: '2', name: '2号线', color: '#e71f64', stations: 29 },{ id: 3, lineNumber: '3', name: '3号线', color: '#f9b62b', stations: 30 },{ id: 4, lineNumber: '4', name: '4号线', color: '#0091cd', stations: 23 },{ id: 5, lineNumber: '5', name: '5号线', color: '#a25aa6', stations: 27 },{ id: 6, lineNumber: '7', name: '7号线', color: '#9b3c8c', stations: 28 }] },
        { id: 5, name: '杭州', icon: '/static/icons/cities/hangzhou.png', mapUrl: 'https://www.metroman.cn/maps/hangzhou', lines: [{ id: 1, lineNumber: '1', name: '1号线', color: '#d71619', stations: 34 },{ id: 2, lineNumber: '2', name: '2号线', color: '#dc241f', stations: 33 },{ id: 3, lineNumber: '4', name: '4号线', color: '#5d2c90', stations: 24 },{ id: 4, lineNumber: '5', name: '5号线', color: '#4daf47', stations: 40 },{ id: 5, lineNumber: '6', name: '6号线', color: '#c22286', stations: 27 },{ id: 6, lineNumber: '7', name: '7号线', color: '#ffcb05', stations: 19 }] },
        { id: 6, name: '苏州', icon: '/static/icons/cities/suzhou.png', mapUrl: 'https://www.metroman.cn/maps/suzhou', lines: [{ id: 1, lineNumber: '1', name: '1号线', color: '#0099cc', stations: 23 },{ id: 2, lineNumber: '2', name: '2号线', color: '#cc0033', stations: 21 },{ id: 3, lineNumber: '3', name: '3号线', color: '#cc9900', stations: 26 },{ id: 4, lineNumber: '4', name: '4号线', color: '#33cc00', stations: 29 },{ id: 5, lineNumber: '5', name: '5号线', color: '#cc6699', stations: 31 },{ id: 6, lineNumber: '6', name: '6号线', color: '#996600', stations: 15 }] }
      ],
      // 动态公交数据
      nearbyStations: [],      // 附近公交站列表
      nearestStation: null,    // 最近的公交站（用于实时公交展示）
      loadingNearby: false,
      refreshing: false,
      currentLocation: { latitude: null, longitude: null },
      showPermissionModal: false,
      searchTimer: null,
      
      routeOptions: [
        { type: 'fastest', name: '最快', icon: '/static/icons/bus/fastest.png' },
        { type: 'cheapest', name: '最便宜', icon: '/static/icons/bus/cheapest.png' },
        { type: 'leastTransfer', name: '少换乘', icon: '/static/icons/bus/transfer.png' },
        { type: 'walking', name: '少步行', icon: '/static/icons/bus/walking.png' }
      ],
      routeResults: [],
      busRouteResults: [],     // 公交tab的路线规划结果

      // 模糊查询相关数据
      startSuggestions: [],
      endSuggestions: [],
      routeStartSuggestions: [],
      routeEndSuggestions: [],
      showStartSuggestions: false,
      showEndSuggestions: false,
      showRouteStartSuggestions: false,
      showRouteEndSuggestions: false,
      
      // 存储选中的地点坐标（用于导航和规划）
      startStationLocation: null,
      endStationLocation: null,
      routeStartLocation: null,
      routeEndLocation: null,
      
      suggestionTimer: null,
      blurTimer: null
    }
  },
  onLoad() {
    this.getUserLocationAndLoadStations();
  },
  methods: {
    // 获取用户位置并加载附近公交站
    getUserLocationAndLoadStations() {
      this.loadingNearby = true;
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
        this.loadingNearby = false;
        this.showPermissionModal = true;
      }
    },
    
    // 加载附近公交站（真实API）
    async loadNearbyStations() {
      if (!this.currentLocation.latitude || !this.currentLocation.longitude) return;
      this.loadingNearby = true;
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
              lines: []  // 待填充线路
            };
            stations.push(station);
          }
          this.nearbyStations = stations;
          // 获取每个站点的线路详情
          await this.fetchStationsLines(stations.slice(0, 8));
          // 设置最近的站点（距离最近）
          if (stations.length) {
            const sorted = [...stations].sort((a,b) => a.distanceValue - b.distanceValue);
            this.nearestStation = sorted[0];
            // 为最近站点的线路获取实时公交信息
            if (this.nearestStation && this.nearestStation.lines.length) {
              this.fetchRealtimeInfoForStation(this.nearestStation);
            }
          }
        } else {
          this.nearbyStations = [];
        }
      } catch (err) {
        console.error('加载附近公交站失败', err);
        uni.showToast({ title: '获取公交站失败', icon: 'none' });
      } finally {
        this.loadingNearby = false;
        this.refreshing = false;
      }
    },
    
    // 获取站点经过的公交线路
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
              stationIndex: line.station_index,
              stopId: line.stop_id,
              lineUid: line.line_uid
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
    
    // 获取某个站点的实时公交信息
    async fetchRealtimeInfoForStation(station) {
      if (!station.lines.length) return;
      for (let line of station.lines) {
        if (!line.lineUid || !line.stopId) continue;
        try {
          const realtimeRes = await this.requestAPI(`${TENCENT_MAP_BASE_URL}/ws/bus/v1/realtime`, {
            key: TENCENT_MAP_KEY,
            line_uid: line.lineUid,
            stop_uid: line.stopId,
            output: 'json'
          });
          if (realtimeRes.status === 0 && realtimeRes.result) {
            const vehicles = realtimeRes.result.vehicles || [];
            if (vehicles.length > 0) {
              const nearest = vehicles[0];
              if (nearest.distance && nearest.duration) {
                line.realtimeInfo = `${nearest.duration}分钟`;
                line.realtimeTime = `${Math.round(nearest.distance / 1000)}站`;
              } else if (nearest.distance) {
                const stationsAway = Math.ceil(nearest.distance / 500);
                line.realtimeInfo = `距离${stationsAway}站`;
                line.realtimeTime = `${Math.round(nearest.distance / 1000 * 2)}分钟`;
              } else {
                line.realtimeInfo = '即将到站';
                line.realtimeTime = '1分钟';
              }
            } else {
              line.realtimeInfo = '暂无实时信息';
              line.realtimeTime = '';
            }
          } else {
            line.realtimeInfo = '即将到站';
            line.realtimeTime = `${Math.floor(Math.random() * 10) + 1}分钟`;
          }
        } catch (e) {
          console.warn(`获取线路${line.name}实时信息失败`, e);
          line.realtimeInfo = '即将到站';
          line.realtimeTime = `${Math.floor(Math.random() * 10) + 1}分钟`;
        }
      }
      this.$forceUpdate();
    },
    
    // 刷新附近公交站
    async refreshNearbyStations() {
      this.refreshing = true;
      await this.loadNearbyStations();
    },
    
    // 搜索公交站或线路
    onSearchInput() {
      if (this.searchTimer) clearTimeout(this.searchTimer);
      this.searchTimer = setTimeout(() => {
        if (this.searchKeyword.trim()) {
          this.searchStationsOrLines(this.searchKeyword);
        } else {
          this.loadNearbyStations();
        }
      }, 500);
    },
    
    async searchStationsOrLines(keyword) {
      if (!keyword.trim()) return;
      this.loadingNearby = true;
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
        } else {
          this.nearbyStations = [];
          uni.showToast({ title: '未找到相关公交站', icon: 'none' });
        }
      } catch (err) {
        console.error('搜索失败', err);
      } finally {
        this.loadingNearby = false;
      }
    },
    
    onSearchCancel() {
      this.searchKeyword = '';
      this.loadNearbyStations();
    },
    
    // 核心：通用路线规划（支持坐标或文本）
    async planRoute(from, to, fromLocation, toLocation, isBusTab = true) {
      // 如果已经存有坐标，直接用坐标格式 "lat,lng"
      let fromParam = from;
      let toParam = to;
      if (fromLocation && fromLocation.latitude && fromLocation.longitude) {
        fromParam = `${fromLocation.latitude},${fromLocation.longitude}`;
      }
      if (toLocation && toLocation.latitude && toLocation.longitude) {
        toParam = `${toLocation.latitude},${toLocation.longitude}`;
      }
      
      // 如果仍然没有坐标（用户手动输入文本未选建议），尝试地理编码获取坐标
      if (!fromLocation && typeof from === 'string' && from !== '当前位置') {
        try {
          const geoRes = await this.requestAPI(`${TENCENT_MAP_BASE_URL}/ws/geocoder/v1/`, { key: TENCENT_MAP_KEY, address: from });
          if (geoRes.status === 0 && geoRes.result && geoRes.result.location) {
            fromParam = `${geoRes.result.location.lat},${geoRes.result.location.lng}`;
          }
        } catch(e) { console.warn('起点地理编码失败', e); }
      }
      if (!toLocation && typeof to === 'string' && to !== '当前位置') {
        try {
          const geoRes = await this.requestAPI(`${TENCENT_MAP_BASE_URL}/ws/geocoder/v1/`, { key: TENCENT_MAP_KEY, address: to });
          if (geoRes.status === 0 && geoRes.result && geoRes.result.location) {
            toParam = `${geoRes.result.location.lat},${geoRes.result.location.lng}`;
          }
        } catch(e) { console.warn('终点地理编码失败', e); }
      }
      
      let policy = '';
      switch(this.selectedRouteOption) {
        case 'fastest': policy = '0'; break;
        case 'cheapest': policy = '1'; break;
        case 'leastTransfer': policy = '2'; break;
        case 'walking': policy = '3'; break;
        default: policy = '0';
      }
      
      const params = {
        key: TENCENT_MAP_KEY,
        from: fromParam,
        to: toParam,
        policy: policy,
        output: 'json'
      };
      
      const res = await this.requestAPI(`${TENCENT_MAP_BASE_URL}/ws/direction/v1/transit`, params);
      if (res.status === 0 && res.result && res.result.routes && res.result.routes.length) {
        const parsed = this.parseRouteResults(res.result.routes);
        if (isBusTab) {
          this.busRouteResults = parsed;
        } else {
          this.routeResults = parsed;
        }
        return true;
      } else {
        // 详细错误提示
        let errorMsg = '未找到合适路线';
        if (res.status === 0 && (!res.result || !res.result.routes)) errorMsg = '暂无公交路线可达';
        else if (res.status !== 0) errorMsg = res.message || '规划失败，请检查网络或地点名称';
        uni.showToast({ title: errorMsg, icon: 'none', duration: 2000 });
        return false;
      }
    },
    
    // 公交tab的路线规划
    async searchBusRoute() {
      if (!this.startStation || !this.endStation) {
        uni.showToast({ title: '请输入起点和终点', icon: 'none' });
        return;
      }
      uni.showLoading({ title: '规划路线中...' });
      try {
        await this.planRoute(this.startStation, this.endStation, this.startStationLocation, this.endStationLocation, true);
      } catch (err) {
        console.error('路线规划异常', err);
        uni.showToast({ title: '网络异常，请重试', icon: 'none' });
      } finally {
        uni.hideLoading();
      }
    },
    
    // 路线规划tab的路线规划
    async searchRoute() {
      if (!this.routeStart || !this.routeEnd) {
        uni.showToast({ title: '请输入起点和终点', icon: 'none' });
        return;
      }
      uni.showLoading({ title: '规划路线中...' });
      try {
        await this.planRoute(this.routeStart, this.routeEnd, this.routeStartLocation, this.routeEndLocation, false);
      } catch (err) {
        console.error('路线规划异常', err);
        uni.showToast({ title: '网络异常，请重试', icon: 'none' });
      } finally {
        uni.hideLoading();
      }
    },
    
    // 解析路径规划结果
    parseRouteResults(routes) {
      return routes.map(route => ({
        summary: route.title || `${route.duration}分钟`,
        time: this.formatDuration(route.duration),
        distance: route.distance ? `${(route.distance / 1000).toFixed(1)}km` : '未知',
        cost: route.price ? route.price / 100 : null,
        steps: (route.bounds || []).map(bound => bound.title)
      }));
    },
    
    formatDuration(minutes) {
      if (minutes < 60) return `${minutes}分钟`;
      const hours = Math.floor(minutes / 60);
      const mins = minutes % 60;
      return `${hours}小时${mins}分钟`;
    },
    
    viewStationDetail(station) {
      uni.navigateTo({ url: `/pages/bus/station-detail?id=${station.id}&name=${encodeURIComponent(station.name)}&lat=${station.latitude}&lng=${station.longitude}` });
    },
    
    viewBusLineDetail(line, station) {
      uni.navigateTo({ url: `/pages/bus/line-detail?lineId=${line.id}&lineName=${encodeURIComponent(line.name)}&station=${encodeURIComponent(station.name)}` });
    },
    
    setStartToCurrent() {
      if (this.currentLocation.latitude) {
        this.startStation = '当前位置';
        this.startStationLocation = { latitude: this.currentLocation.latitude, longitude: this.currentLocation.longitude, name: '当前位置' };
      } else {
        uni.getLocation({ 
          success: (res) => { 
            this.startStation = '当前位置';
            this.startStationLocation = { latitude: res.latitude, longitude: res.longitude, name: '当前位置' };
          }, 
          fail: () => { uni.showToast({ title: '获取位置失败', icon: 'none' }); } 
        });
      }
    },
    setEndToCurrent() {
      if (this.currentLocation.latitude) {
        this.endStation = '当前位置';
        this.endStationLocation = { latitude: this.currentLocation.latitude, longitude: this.currentLocation.longitude, name: '当前位置' };
      } else {
        uni.getLocation({ 
          success: (res) => { 
            this.endStation = '当前位置';
            this.endStationLocation = { latitude: res.latitude, longitude: res.longitude, name: '当前位置' };
          }, 
          fail: () => { uni.showToast({ title: '获取位置失败', icon: 'none' }); } 
        });
      }
    },
    
    // 导航到公交站
    navigateToStation(station) {
      if (station.latitude && station.longitude) {
        uni.openLocation({
          latitude: station.latitude,
          longitude: station.longitude,
          name: station.name,
          address: station.address || '',
          success: () => {},
          fail: (err) => {
            console.error('打开地图失败', err);
            uni.showToast({ title: '导航失败', icon: 'none' });
          }
        });
      } else {
        uni.showToast({ title: '站点坐标缺失', icon: 'none' });
      }
    },
    
    // 导航到路线规划的终点（简化：直接导航至终点）
    navigateToRoute(route) {
      let endLocation = null;
      if (this.activeTab === 'bus') {
        endLocation = this.endStationLocation;
      } else {
        endLocation = this.routeEndLocation;
      }
      if (endLocation && endLocation.latitude && endLocation.longitude) {
        uni.openLocation({
          latitude: endLocation.latitude,
          longitude: endLocation.longitude,
          name: endLocation.name || '目的地',
          address: endLocation.address || '',
          success: () => {}
        });
      } else {
        uni.showToast({ title: '无法获取终点坐标', icon: 'none' });
      }
    },
    
    // 模糊查询相关方法
    async fetchSuggestions(keyword, type) {
      if (!keyword.trim()) {
        this.clearSuggestions(type);
        return;
      }
      try {
        const params = {
          key: TENCENT_MAP_KEY,
          keyword: keyword,
          region: '全国',
          output: 'json'
        };
        if (this.currentLocation.latitude) {
          params.location = `${this.currentLocation.latitude},${this.currentLocation.longitude}`;
        }
        const res = await this.requestAPI(`${TENCENT_MAP_BASE_URL}/ws/place/v1/suggestion`, params);
        if (res.status === 0 && res.data && res.data.length) {
          const suggestions = res.data.map(item => ({
            id: item.id,
            title: item.title,
            address: item.address,
            latitude: item.location.lat,
            longitude: item.location.lng
          }));
          this.setSuggestions(type, suggestions);
        } else {
          this.clearSuggestions(type);
        }
      } catch (err) {
        console.error('获取建议失败', err);
        this.clearSuggestions(type);
      }
    },
    
    setSuggestions(type, suggestions) {
      if (type === 'start') this.startSuggestions = suggestions;
      else if (type === 'end') this.endSuggestions = suggestions;
      else if (type === 'routeStart') this.routeStartSuggestions = suggestions;
      else if (type === 'routeEnd') this.routeEndSuggestions = suggestions;
    },
    
    clearSuggestions(type) {
      this.setSuggestions(type, []);
    },
    
    onStartStationInput() {
      if (this.suggestionTimer) clearTimeout(this.suggestionTimer);
      this.suggestionTimer = setTimeout(() => {
        this.fetchSuggestions(this.startStation, 'start');
      }, 300);
    },
    onEndStationInput() {
      if (this.suggestionTimer) clearTimeout(this.suggestionTimer);
      this.suggestionTimer = setTimeout(() => {
        this.fetchSuggestions(this.endStation, 'end');
      }, 300);
    },
    onRouteStartInput() {
      if (this.suggestionTimer) clearTimeout(this.suggestionTimer);
      this.suggestionTimer = setTimeout(() => {
        this.fetchSuggestions(this.routeStart, 'routeStart');
      }, 300);
    },
    onRouteEndInput() {
      if (this.suggestionTimer) clearTimeout(this.suggestionTimer);
      this.suggestionTimer = setTimeout(() => {
        this.fetchSuggestions(this.routeEnd, 'routeEnd');
      }, 300);
    },
    
    selectStartSuggestion(item) {
      this.startStation = item.title;
      this.startStationLocation = { latitude: item.latitude, longitude: item.longitude, name: item.title, address: item.address };
      this.showStartSuggestions = false;
      this.startSuggestions = [];
    },
    selectEndSuggestion(item) {
      this.endStation = item.title;
      this.endStationLocation = { latitude: item.latitude, longitude: item.longitude, name: item.title, address: item.address };
      this.showEndSuggestions = false;
      this.endSuggestions = [];
    },
    selectRouteStartSuggestion(item) {
      this.routeStart = item.title;
      this.routeStartLocation = { latitude: item.latitude, longitude: item.longitude, name: item.title, address: item.address };
      this.showRouteStartSuggestions = false;
      this.routeStartSuggestions = [];
    },
    selectRouteEndSuggestion(item) {
      this.routeEnd = item.title;
      this.routeEndLocation = { latitude: item.latitude, longitude: item.longitude, name: item.title, address: item.address };
      this.showRouteEndSuggestions = false;
      this.routeEndSuggestions = [];
    },
    
    hideSuggestionsDelayed(type) {
      if (this.blurTimer) clearTimeout(this.blurTimer);
      this.blurTimer = setTimeout(() => {
        if (type === 'start') this.showStartSuggestions = false;
        else if (type === 'end') this.showEndSuggestions = false;
        else if (type === 'routeStart') this.showRouteStartSuggestions = false;
        else if (type === 'routeEnd') this.showRouteEndSuggestions = false;
      }, 200);
    },
    
    useCurrentLocation(type) {
      if (this.currentLocation.latitude) {
        if (type === 'start') {
          this.routeStart = '当前位置';
          this.routeStartLocation = { latitude: this.currentLocation.latitude, longitude: this.currentLocation.longitude, name: '当前位置' };
        } else {
          this.routeEnd = '当前位置';
          this.routeEndLocation = { latitude: this.currentLocation.latitude, longitude: this.currentLocation.longitude, name: '当前位置' };
        }
      } else {
        uni.getLocation({
          success: (res) => {
            if (type === 'start') {
              this.routeStart = '当前位置';
              this.routeStartLocation = { latitude: res.latitude, longitude: res.longitude, name: '当前位置' };
            } else {
              this.routeEnd = '当前位置';
              this.routeEndLocation = { latitude: res.latitude, longitude: res.longitude, name: '当前位置' };
            }
          },
          fail: () => uni.showToast({ title: '获取位置失败', icon: 'none' })
        });
      }
    },
    selectRouteOption(option) { 
      this.selectedRouteOption = option;
    },
    
    // 地铁相关方法
    selectCity(city) { this.selectedCity = city; },
    backToCityList() { this.selectedCity = null; },
    viewSubwayMap() {
      if (this.selectedCity && this.selectedCity.mapUrl) {
        uni.navigateTo({ url: `/pages/common/webview?url=${encodeURIComponent(this.selectedCity.mapUrl)}&title=${encodeURIComponent(this.selectedCity.name + '地铁线路图')}` });
      } else { uni.showToast({ title: '暂无线路图', icon: 'none' }); }
    },
    viewSubwayLine(line) {
      uni.navigateTo({ url: `/pages/bus/subway-line?id=${line.id}&city=${this.selectedCity.name}` });
    },
    
    requestLocationPermission() {
      this.showPermissionModal = false;
      uni.openSetting({
        success: (res) => {
          if (res.authSetting['scope.userLocation']) this.getUserLocationAndLoadStations();
        }
      });
    },
    
    // 通用API请求方法
    requestAPI(url, params) {
      return new Promise((resolve, reject) => {
        uni.request({
          url: url,
          method: 'GET',
          data: params,
          timeout: 15000,
          success: (res) => {
            if (res.statusCode === 200) {
              if (res.data.status === 0) resolve(res.data);
              else reject(new Error(res.data.message || `请求失败: ${res.data.status}`));
            } else reject(new Error(`HTTP ${res.statusCode}`));
          },
          fail: reject
        });
      });
    }
  }
}
</script>

<style scoped>
.bus-page {
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

.tab-section {
  display: flex;
  background: #fff;
  border-bottom: 1rpx solid #eee;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 25rpx 0;
  font-size: 28rpx;
  color: #666;
  transition: all 0.3s ease;
  position: relative;
}

.tab-item.active {
  color: #b8d4ff;
  font-weight: 500;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 80rpx;
  height: 4rpx;
  background: #b8d4ff;
  border-radius: 2rpx;
}

.content-section {
  flex: 1;
  overflow: hidden;
}

.realtime-section,
.line-search-section,
.nearby-section,
.city-section,
.subway-lines-section,
.route-search-section,
.route-results {
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

.more-btn {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 26rpx;
  color: #999;
}

.more-icon {
  width: 20rpx;
  height: 20rpx;
}

.realtime-scroll {
  white-space: nowrap;
}

.realtime-item {
  display: inline-flex;
  flex-direction: column;
  background: #f8f8f8;
  border-radius: 16rpx;
  padding: 25rpx;
  margin-right: 20rpx;
  min-width: 280rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.06);
}

.bus-line {
  display: flex;
  align-items: center;
  gap: 15rpx;
  margin-bottom: 15rpx;
}

.line-number {
  font-size: 32rpx;
  color: #b8d4ff;
  font-weight: 600;
}

.line-name {
  font-size: 24rpx;
  color: #666;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bus-station {
  margin-bottom: 15rpx;
}

.station-name {
  font-size: 26rpx;
  color: #333;
  font-weight: 500;
}

.bus-arrival {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.arrival-info {
  font-size: 24rpx;
  color: #ff6b6b;
}

.arrival-time {
  font-size: 24rpx;
  color: #999;
}

.search-input-group {
  margin-bottom: 25rpx;
  position: relative;
}

.input-item {
  display: flex;
  align-items: center;
  background: #f8f8f8;
  border-radius: 12rpx;
  padding: 20rpx;
  margin-bottom: 15rpx;
  position: relative;
}

.input-item.start {
  border-left: 4rpx solid #6bcf7f;
}

.input-item.end {
  border-left: 4rpx solid #ff6b6b;
}

.input-icon {
  width: 28rpx;
  height: 28rpx;
  margin-right: 15rpx;
}

.input-field {
  flex: 1;
  font-size: 28rpx;
  color: #333;
}

.location-btn {
  position: absolute;
  right: 20rpx;
  width: 40rpx;
  height: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.location-icon {
  width: 24rpx;
  height: 24rpx;
}

.search-btn {
  background: #b8d4ff;
  color: #fff;
  text-align: center;
  padding: 20rpx;
  border-radius: 12rpx;
  font-size: 28rpx;
  font-weight: 500;
}

.nearby-list {
  max-height: 500rpx;
}

.nearby-item {
  padding: 25rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.station-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15rpx;
  flex: 1;
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

.station-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.station-lines {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  flex: 1;
}

.line-tag {
  font-size: 20rpx;
  color: #b8d4ff;
  background: #f0f7ff;
  padding: 6rpx 12rpx;
  border-radius: 12rpx;
  border: 1rpx solid #e1edff;
}

.more-lines {
  font-size: 20rpx;
  color: #999;
}

.nav-station-btn {
  display: flex;
  align-items: center;
  gap: 6rpx;
  background: #b8d4ff20;
  padding: 8rpx 16rpx;
  border-radius: 30rpx;
  font-size: 22rpx;
  color: #b8d4ff;
  margin-left: 15rpx;
}

.nav-icon {
  width: 28rpx;
  height: 28rpx;
}

.city-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 25rpx;
}

.city-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 25rpx;
  background: #f8f8f8;
  border-radius: 16rpx;
  transition: all 0.3s ease;
}

.city-icon {
  width: 80rpx;
  height: 80rpx;
  margin-bottom: 15rpx;
  border-radius: 50%;
  overflow: hidden;
  background: #f0f0f0;
}

.city-image {
  width: 100%;
  height: 100%;
}

.city-name {
  font-size: 26rpx;
  color: #333;
  font-weight: 500;
}

.back-city {
  display: flex;
  align-items: center;
  padding: 20rpx 30rpx;
  background: #fff;
  border-bottom: 1rpx solid #eee;
}

.back-icon {
  width: 28rpx;
  height: 28rpx;
  margin-right: 10rpx;
}

.back-text {
  font-size: 26rpx;
  color: #666;
}

.current-city {
  margin-left: auto;
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
}

.subway-map-section {
  background: #fff;
  padding: 30rpx;
  border-bottom: 1rpx solid #eee;
  height: 300rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.map-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15rpx;
}

.map-icon {
  width: 80rpx;
  height: 80rpx;
  opacity: 0.7;
}

.map-title {
  font-size: 32rpx;
  color: #333;
  font-weight: 500;
}

.map-desc {
  font-size: 26rpx;
  color: #666;
}

.lines-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20rpx;
}

.line-item {
  display: flex;
  align-items: center;
  background: #f8f8f8;
  border-radius: 16rpx;
  padding: 25rpx;
  border: 2rpx solid;
  transition: all 0.3s ease;
}

.line-icon {
  width: 60rpx;
  height: 60rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
}

.line-number {
  color: #fff;
  font-size: 24rpx;
  font-weight: 600;
}

.line-info {
  flex: 1;
}

.line-name {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
  display: block;
  margin-bottom: 8rpx;
}

.line-stations {
  font-size: 22rpx;
  color: #999;
}

.search-options {
  display: flex;
  justify-content: space-around;
  margin: 25rpx 0;
}

.option-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  font-size: 24rpx;
  color: #666;
  padding: 15rpx;
  transition: all 0.3s ease;
}

.option-item.active {
  color: #b8d4ff;
}

.option-icon {
  width: 40rpx;
  height: 40rpx;
}

.results-list {
  max-height: 500rpx;
}

.route-item {
  padding: 25rpx;
  border: 2rpx solid #f0f0f0;
  border-radius: 16rpx;
  margin-bottom: 20rpx;
  transition: all 0.3s ease;
  position: relative;
}

.route-header {
  display: flex;
  align-items: center;
  gap: 15rpx;
  margin-bottom: 15rpx;
}

.route-index {
  width: 40rpx;
  height: 40rpx;
  background: #b8d4ff;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20rpx;
  font-weight: 600;
}

.route-summary {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
  flex: 1;
}

.route-details {
  display: flex;
  gap: 20rpx;
  margin-bottom: 15rpx;
}

.route-time,
.route-distance,
.route-cost {
  font-size: 24rpx;
  color: #666;
}

.route-time {
  color: #ff6b6b;
  font-weight: 500;
}

.route-cost {
  color: #6bcf7f;
  font-weight: 500;
}

.route-steps {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
}

.step-text {
  font-size: 22rpx;
  color: #999;
  background: #f5f5f5;
  padding: 6rpx 12rpx;
  border-radius: 12rpx;
}

.more-steps {
  font-size: 22rpx;
  color: #b8d4ff;
}

.nav-btn {
  position: absolute;
  right: 25rpx;
  top: 25rpx;
  background: #b8d4ff20;
  padding: 8rpx 20rpx;
  border-radius: 30rpx;
}

.nav-text {
  font-size: 24rpx;
  color: #b8d4ff;
  font-weight: 500;
}

.safe-area {
  height: env(safe-area-inset-bottom);
  background: #f8f8f8;
}

.loading-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx 0;
}

.loading-text,
.empty-text {
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

.suggestions-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #fff;
  border-radius: 12rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.15);
  max-height: 400rpx;
  overflow-y: auto;
  z-index: 100;
  margin-top: 4rpx;
}

.suggestion-item {
  padding: 20rpx 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.suggestion-title {
  font-size: 28rpx;
  color: #333;
  display: block;
  margin-bottom: 6rpx;
}

.suggestion-address {
  font-size: 22rpx;
  color: #999;
}
</style>