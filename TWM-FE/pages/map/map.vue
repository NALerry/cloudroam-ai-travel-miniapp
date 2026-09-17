<template>
  <view class="map-page">
    <!-- 顶部搜索栏（优化后） -->
    <view class="search-section">
      <view class="search-bar-container">
        <view class="search-bar" @tap="onSearchFocus">
          <view class="search-icon-wrapper">
            <image class="search-icon" src="/static/icons/general/search.png" mode="aspectFit"></image>
          </view>
          <input 
            class="search-input" 
            :placeholder="searchPlaceholder"
            :value="searchKeyword"
            @input="onSearchInput"
            @confirm="onSearchConfirm"
            disabled
          />
          <view class="search-clear" v-if="searchKeyword" @tap.stop="clearSearch">
            <image class="clear-icon" src="/static/icons/general/close.png" mode="aspectFit"></image>
          </view>
          <view class="search-voice" v-if="!searchKeyword">
            <image class="voice-icon" src="/static/icons/general/voice.png" mode="aspectFit"></image>
          </view>
        </view>
      </view>
    </view>

    <!-- 搜索结果面板（优化后） -->
    <view class="search-results-panel" v-if="showSearchResults && searchResults.length > 0">
      <view class="search-results-header">
        <text class="results-title">搜索结果</text>
        <view class="results-close" @tap="hideSearchResults">
          <image class="close-icon" src="/static/icons/general/close.png" mode="aspectFit"></image>
        </view>
      </view>
      <scroll-view class="search-results-list" scroll-y>
        <view 
          class="search-result-item" 
          v-for="item in searchResults" 
          :key="item.id"
          @tap="selectSearchResult(item)"
        >
          <view class="result-icon">
            <view class="result-icon-inner">
              <image class="location-icon" src="/static/icons/general/location.png" mode="aspectFit"></image>
            </view>
          </view>
          <view class="result-content">
            <text class="result-title">{{ item.title }}</text>
            <text class="result-address">{{ item.address }}</text>
            <view class="result-tags">
              <text class="result-region">{{ item.province }}{{ item.city }}{{ item.district }}</text>
            </view>
          </view>
          <view class="result-distance" v-if="item.distance">
            <text>{{ item.distance }}</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 功能按钮区域 -->
    <view class="function-buttons">
      <view class="button-row">
        <view 
          class="function-button" 
          v-for="item in firstRowButtons" 
          :key="item.id"
          @tap="onFunctionButtonTap(item)"
        >
          <view class="button-icon" :style="{ backgroundColor: item.bgColor }">
            <image class="icon-image" :src="item.icon" mode="aspectFit"></image>
          </view>
          <text class="button-text">{{ item.name }}</text>
        </view>
      </view>
      <view class="button-row">
        <view 
          class="function-button" 
          v-for="item in secondRowButtons" 
          :key="item.id"
          @tap="onFunctionButtonTap(item)"
        >
          <view class="button-icon" :style="{ backgroundColor: item.bgColor }">
            <image class="icon-image" :src="item.icon" mode="aspectFit"></image>
          </view>
          <text class="button-text">{{ item.name }}</text>
        </view>
      </view>
    </view>

    <!-- 优化后的整体滑动容器 -->
    <scroll-view 
      class="main-scroll" 
      scroll-y 
      :scroll-top="scrollTop"
      @scroll="onScroll"
      :show-scrollbar="false"
      :enhanced="true"
      :bounces="true"
    >
      <!-- 地图容器 - 可随页面滚动 -->
      <view class="map-container" :style="{ height: mapHeight + 'px' }">
        <map 
          id="travelMap"
          :latitude="mapCenter.latitude"
          :longitude="mapCenter.longitude"
          :markers="markers"
          :polyline="polylines"
          :scale="mapScale"
          :show-location="true"
          :enable-zoom="true"
          :enable-scroll="true"
          :enable-rotate="false"
          :enable-overlooking="false"
          @regionchange="onRegionChange"
          @markertap="onMarkerTap"
          @callouttap="onCalloutTap"
          @tap="onMapTap"
          class="map"
          style="width: 100%; height: 100%;"
        ></map>
        
        <!-- 地图控制按钮 -->
        <view class="map-controls">
          <view class="control-btn zoom-in" @tap="zoomIn">
            <image class="control-icon" src="/static/icons/general/zoom-in.png" mode="aspectFit"></image>
          </view>
          <view class="control-btn zoom-out" @tap="zoomOut">
            <image class="control-icon" src="/static/icons/general/zoom-out.png" mode="aspectFit"></image>
          </view>
          <view class="control-btn locate" @tap="locateMe">
            <image class="control-icon" src="/static/icons/general/navigation.png" mode="aspectFit"></image>
          </view>
          <view class="control-btn view-all" @tap="focusOnRoute" v-if="currentRoute.length > 0">
            <image class="control-icon" src="/static/icons/general/view-all.png" mode="aspectFit"></image>
          </view>
        </view>

        <!-- 定位状态显示 -->
        <view class="location-status" v-if="locationStatus">
          <text class="status-text">{{ locationStatus }}</text>
        </view>

        <!-- 添加地点提示 -->
        <view class="add-point-tip" v-if="showAddPointTip">
          <text>点击地图添加地点，或使用搜索功能</text>
          <view class="tip-close" @tap="hideAddPointTip">
            <image class="close-icon" src="/static/icons/general/close.png" mode="aspectFit"></image>
          </view>
        </view>
      </view>

      <!-- 信息面板内容 -->
      <view class="content-panel">
        <!-- 路线规划 -->
        <view class="route-section">
          <view class="section-header">
            <text class="section-title">路线规划</text>
            <view class="route-actions">
              <view class="action-btn" @tap="showRouteOptions">
                <image class="action-icon" src="/static/icons/general/path.png" mode="aspectFit"></image>
                <text>规划路线</text>
              </view>
              <view class="action-btn clear" @tap="clearRoute" :class="{ disabled: currentRoute.length === 0 }">
                <image class="action-icon" src="/static/icons/general/clean.png" mode="aspectFit"></image>
                <text>清除</text>
              </view>
              <view class="action-btn my-routes" @tap="goToMyRoutes">
                <image class="action-icon" src="/static/icons/general/list.png" mode="aspectFit"></image>
                <text>我的行程</text>
              </view>
            </view>
          </view>
          
          <view class="route-selector" v-if="savedRoutes.length > 0">
            <view class="selector-header">
              <text class="selector-title">选择行程规划</text>
              <view class="selector-actions">
                <view class="selector-btn refresh" @tap="loadSavedRoutes">
                  <image class="selector-icon" src="/static/icons/general/refresh.png" mode="aspectFit"></image>
                  <text>刷新</text>
                </view>
              </view>
            </view>
            <scroll-view class="route-selector-list" scroll-x :show-scrollbar="false">
              <view 
                class="route-selector-item" 
                v-for="route in savedRoutes" 
                :key="route.id"
                :class="{ active: selectedRouteId === route.id }"
                @tap="selectSavedRoute(route)"
              >
                <view class="route-selector-content">
                  <text class="route-selector-name">{{ route.name }}</text>
                  <text class="route-selector-info">{{ route.places.length }}个地点 · {{ route.duration }}天</text>
                  <view class="route-selector-tags">
                    <text class="route-tag" v-for="tag in route.tags.slice(0, 2)" :key="tag">{{ tag }}</text>
                  </view>
                </view>
                <view class="route-selector-actions">
                  <view class="route-action-btn view" @tap.stop="viewRouteDetail(route.id)">
                    <image class="action-icon" src="/static/icons/general/eye.png" mode="aspectFit"></image>
                  </view>
                  <view class="route-action-btn delete" @tap.stop="deleteSavedRoute(route.id)">
                    <image class="action-icon" src="/static/icons/general/delete.png" mode="aspectFit"></image>
                  </view>
                </view>
              </view>
            </scroll-view>
          </view>
          
          <view class="route-content" v-if="currentRoute.length > 0">
            <view class="current-route-header">
              <text class="current-route-title">当前路线</text>
              <text class="current-route-count">{{ currentRoute.length }}个地点</text>
            </view>
            
            <!-- 新增：起点与终点选择器（仅从当前路线地点中选择） -->
            <view class="start-end-selector" v-if="currentRoute.length >= 2">
              <view class="selector-row">
                <text class="selector-label">起点</text>
                <picker :range="routeOptions" :range-key="'name'" :value="selectedStartIndex" @change="onStartChange">
                  <view class="picker-content">{{ routeOptions[selectedStartIndex]?.name || '请选择起点' }}</view>
                </picker>
              </view>
              <view class="selector-row">
                <text class="selector-label">终点</text>
                <picker :range="routeOptions" :range-key="'name'" :value="selectedEndIndex" @change="onEndChange">
                  <view class="picker-content">{{ routeOptions[selectedEndIndex]?.name || '请选择终点' }}</view>
                </picker>
              </view>
              <view class="apply-order-btn" @tap="applyStartEndOrder">
                <text>应用为路线顺序</text>
              </view>
            </view>
            
            <scroll-view class="route-list" scroll-x :show-scrollbar="false">
              <view 
                class="route-item" 
                v-for="(point, index) in currentRoute" 
                :key="point.id"
                :class="{ active: index === activeRouteIndex }"
                @tap="focusOnPoint(point, index)"
              >
                <view class="route-order">{{ index + 1 }}</view>
                <text class="route-name">{{ point.name }}</text>
                <view class="route-weather" @tap.stop="goToWeather(point)">
                  <image class="weather-icon" src="/static/icons/general/weather.png" mode="aspectFit"></image>
                  <text>{{ point.temperature }}</text>
                </view>
                <view class="route-actions" v-if="currentRoute.length > 1">
                  <view class="route-action-btn" @tap.stop="removePoint(index)">
                    <image class="action-icon" src="/static/icons/general/close.png" mode="aspectFit"></image>
                  </view>
                </view>
              </view>
            </scroll-view>
            
            <view class="route-suggestion">
              <text class="suggestion-title">推荐出行方式：</text>
              <view class="transport-options">
                <view 
                  class="transport-option" 
                  v-for="option in transportOptions" 
                  :key="option.type"
                  :class="{ active: selectedTransport === option.type }"
                  @tap="selectTransport(option.type)"
                >
                  <image class="transport-icon" :src="option.icon" mode="aspectFit"></image>
                  <text>{{ option.name }}</text>
                  <text class="transport-time">{{ option.time }}</text>
                </view>
              </view>
            </view>

            <view class="route-details" v-if="selectedTransport && routeDetails[selectedTransport]">
              <view class="route-details-header">
                <text class="details-title">{{ getTransportName(selectedTransport) }}出行方案</text>
                <view class="details-summary">
                  <text class="summary-item">总距离: {{ routeDetails[selectedTransport].distance }}</text>
                  <text class="summary-item">预计时间: {{ routeDetails[selectedTransport].duration }}</text>
                  <text class="summary-item" v-if="routeDetails[selectedTransport].cost">预计费用: {{ routeDetails[selectedTransport].cost }}</text>
                </view>
              </view>
              
              <scroll-view class="route-steps" scroll-y>
                <view 
                  class="route-step" 
                  v-for="(step, index) in routeDetails[selectedTransport].steps" 
                  :key="index"
                >
                  <view class="step-number">{{ index + 1 }}</view>
                  <view class="step-content">
                    <text class="step-instruction">{{ step.instruction }}</text>
                    <text class="step-distance" v-if="step.distance">{{ step.distance }}</text>
                  </view>
                </view>
              </scroll-view>
            </view>

            <view class="route-operations">
              <view class="operation-btn save" @tap="saveRoute" :class="{ disabled: currentRoute.length === 0 }">
                <image class="operation-icon" src="/static/icons/general/save.png" mode="aspectFit"></image>
                <text>保存路线</text>
              </view>
              <view class="operation-btn share" @tap="shareRoute" :class="{ disabled: currentRoute.length === 0 }">
                <image class="operation-icon" src="/static/icons/general/share.png" mode="aspectFit"></image>
                <text>分享路线</text>
              </view>
            </view>
          </view>
          
          <view class="empty-route" v-else-if="savedRoutes.length === 0">
            <image class="empty-icon" src="/static/icons/general/empty.png" mode="aspectFit"></image>
            <text class="empty-text">暂无路线，点击"规划路线"开始规划</text>
            <text class="empty-desc">添加地点后可以规划路线并保存</text>
            <view class="empty-action" @tap="goToMyRoutes">
              <text class="empty-action-text">查看我的行程规划</text>
            </view>
          </view>
        </view>

        <!-- 网友攻略 -->
        <view class="strategy-section">
          <view class="section-header">
            <text class="section-title">网友攻略推荐</text>
            <view class="more-btn" @tap="viewMoreStrategies">
              <text>更多</text>
              <image class="more-icon" src="/static/icons/general/more.png" mode="aspectFit"></image>
            </view>
          </view>
          
          <scroll-view class="strategy-list" scroll-x :show-scrollbar="false">
            <view 
              class="strategy-item" 
              v-for="strategy in strategies" 
              :key="strategy.id"
              @tap="viewStrategy(strategy)"
            >
              <view class="strategy-badge" :class="strategy.badgeType">{{ strategy.badgeText }}</view>
              <image class="strategy-image" :src="strategy.cover" mode="aspectFill"></image>
              <view class="strategy-info">
                <text class="strategy-title">{{ strategy.title }}</text>
                <view class="strategy-meta">
                  <view class="author-info">
                    <image class="author-avatar" :src="strategy.avatar" mode="aspectFill"></image>
                    <text class="author">{{ strategy.author }}</text>
                  </view>
                  <view class="likes-count">
                    <image class="like-icon" src="/static/icons/general/like.png" mode="aspectFit"></image>
                    <text>{{ strategy.likes }}</text>
                  </view>
                </view>
              </view>
            </view>
          </scroll-view>
        </view>

        <!-- 附近推荐 -->
        <view class="nearby-section">
          <view class="section-header">
            <text class="section-title">附近推荐</text>
            <view class="more-btn" @tap="viewMoreNearby">
              <text>更多</text>
              <image class="more-icon" src="/static/icons/general/more.png" mode="aspectFit"></image>
            </view>
          </view>
          
          <view class="nearby-grid">
            <view 
              class="nearby-item" 
              v-for="item in nearbyPlaces" 
              :key="item.id"
              @tap="viewNearbyPlace(item)"
            >
              <image class="nearby-image" :src="item.image" mode="aspectFill"></image>
              <view class="nearby-info">
                <text class="nearby-name">{{ item.name }}</text>
                <text class="nearby-type">{{ item.type }}</text>
                <view class="nearby-distance">
                  <image class="distance-icon" src="/static/icons/general/distance.png" mode="aspectFit"></image>
                  <text>{{ item.distance }}</text>
                </view>
              </view>
            </view>
          </view>
        </view>

        <!-- 底部安全区域 -->
        <view class="safe-area"></view>
      </view>
    </scroll-view>

    <!-- 搜索页面（优化后） -->
    <view class="search-page" v-if="showSearchPage">
      <view class="search-page-header">
        <view class="search-page-bar">
          <view class="back-btn" @tap="hideSearchPage">
            <image class="back-icon" src="/static/icons/general/back.png" mode="aspectFit"></image>
          </view>
          <view class="search-input-container">
            <image class="search-input-icon" src="/static/icons/general/search.png" mode="aspectFit"></image>
            <input 
              class="search-page-input" 
              placeholder="搜索地点或景点"
              v-model="searchKeyword"
              @input="onSearchInput"
              @confirm="onSearchConfirm"
              focus
            />
            <view class="search-page-clear" v-if="searchKeyword" @tap="clearSearch">
              <image class="clear-icon" src="/static/icons/general/close.png" mode="aspectFit"></image>
            </view>
          </view>
          <view class="search-btn" @tap="doSearch">
            <text>搜索</text>
          </view>
        </view>
      </view>

      <view class="search-history" v-if="!showSearchResults && searchHistory.length > 0">
        <view class="history-header">
          <text class="history-title">搜索历史</text>
          <view class="clear-history" @tap="clearSearchHistory">
            <image class="clear-icon" src="/static/icons/general/delete.png" mode="aspectFit"></image>
          </view>
        </view>
        <view class="history-list">
          <view 
            class="history-item" 
            v-for="item in searchHistory" 
            :key="item"
            @tap="searchFromHistory(item)"
          >
            <image class="history-icon" src="/static/icons/general/history.png" mode="aspectFit"></image>
            <text class="history-text">{{ item }}</text>
          </view>
        </view>
      </view>

      <view class="hot-search" v-if="!showSearchResults && !searchKeyword">
        <view class="hot-header">
          <text class="hot-title">热门搜索</text>
        </view>
        <view class="hot-list">
          <view 
            class="hot-item" 
            v-for="item in hotSearchList" 
            :key="item"
            @tap="searchFromHot(item)"
          >
            <text class="hot-text">{{ item }}</text>
          </view>
        </view>
      </view>

      <view class="search-page-results" v-if="showSearchResults">
        <view class="search-results-header">
          <text class="results-title">搜索结果 ({{ searchResults.length }})</text>
          <view class="results-tips" v-if="isSearching">
            <text>搜索中...</text>
          </view>
        </view>
        <scroll-view class="search-page-results-list" scroll-y>
          <view 
            class="search-page-result-item" 
            v-for="item in searchResults" 
            :key="item.id"
            @tap="selectSearchResult(item)"
          >
            <view class="result-icon">
              <view class="result-icon-inner">
                <image class="location-icon" src="/static/icons/general/location.png" mode="aspectFit"></image>
              </view>
            </view>
            <view class="result-content">
              <text class="result-title">{{ item.title }}</text>
              <text class="result-address">{{ item.address }}</text>
              <view class="result-tags">
                <text class="result-region">{{ item.province }}{{ item.city }}{{ item.district }}</text>
              </view>
            </view>
            <view class="result-distance" v-if="item.distance">
              <text>{{ item.distance }}</text>
            </view>
          </view>
        </scroll-view>
        
        <view class="no-results" v-if="!isSearching && searchResults.length === 0 && searchKeyword">
          <image class="no-results-icon" src="/static/icons/general/empty.png" mode="aspectFit"></image>
          <text class="no-results-text">未找到相关地点</text>
          <text class="no-results-desc">请尝试其他关键词</text>
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
          <text class="permission-text">为了提供精准的定位和路线规划服务，需要获取您的位置信息</text>
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
const TENCENT_MAP_KEY = '';
const TENCENT_MAP_BASE_URL = 'https://apis.map.qq.com';

export default {
  data() {
    return {
      searchPlaceholder: '搜索地点或景点',
      searchKeyword: '',
      showSearchPage: false,
      showSearchResults: false,
      isSearching: false,
      mapContext: null,
      mapCenter: {
        latitude: 39.916, // 默认北京坐标
        longitude: 116.397
      },
      mapScale: 15,
      mapHeight: 400,
      scrollTop: 0,
      showAddPointTip: false,
      showPermissionModal: false,
      locationStatus: '',
      // 心知天气 API 配置
      seniverseKey: 'SX7GLnDy1bUNd-1XG',
      seniverseBaseUrl: 'https://api.seniverse.com/v3/weather/now.json',
      // 新增：行程规划相关数据
      savedRoutes: [],
      selectedRouteId: null,
      // 新增：出行方案详情数据
      routeDetails: {
        walk: null,
        bike: null,
        bus: null,
        drive: null
      },
      // 搜索相关数据
      searchResults: [],
      searchHistory: [],
      hotSearchList: ['故宫', '天安门', '颐和园', '长城', '王府井', '南锣鼓巷', '鸟巢', '水立方'],
      // 第一排功能按钮
      firstRowButtons: [
        { 
          id: 1, 
          name: '加油站', 
          icon: '/static/icons/general/gas-station.png', 
          type: 'gas',
          bgColor: '#FFF0F0'
        },
        { 
          id: 2, 
          name: '酒店', 
          icon: '/static/icons/general/hotel.png', 
          type: 'hotel',
          bgColor: '#F0F7FF'
        },
        { 
          id: 3, 
          name: '美食', 
          icon: '/static/icons/general/restaurant.png', 
          type: 'food',
          bgColor: '#FFF7E6'
        },
        { 
          id: 4, 
          name: '景点门票', 
          icon: '/static/icons/general/ticket.png', 
          type: 'ticket',
          bgColor: '#F0FFF4'
        },
        { 
          id: 5, 
          name: '购物', 
          icon: '/static/icons/general/shopping.png', 
          type: 'shopping',
          bgColor: '#F9F0FF'
        }
      ],
      // 第二排功能按钮
      secondRowButtons: [
        { 
          id: 6, 
          name: '公交/地铁', 
          icon: '/static/icons/general/subway.png', 
          type: 'bus',
          bgColor: '#E6F7FF'
        },
        { 
          id: 7, 
          name: '实时公交', 
          icon: '/static/icons/general/bus.png', 
          type: 'realtime-bus',
          bgColor: '#F6FFED'
        },
        { 
          id: 8, 
          name: '骑行', 
          icon: '/static/icons/general/bike.png', 
          type: 'bike',
          bgColor: '#FFF2E8'
        },
        { 
          id: 9, 
          name: '打车', 
          icon: '/static/icons/general/taxi.png', 
          type: 'taxi',
          bgColor: '#F9F0FF'
        },
        { 
          id: 10, 
          name: '路线', 
          icon: '/static/icons/general/path.png', 
          type: 'route',
          bgColor: '#E8F1FF'
        }
      ],
      // 地图标记点
      markers: [],
      // 路线折线（支持多条）
      polylines: [],
      // 当前路线
      currentRoute: [],
      activeRouteIndex: 0,
      // 出行方式选项
      transportOptions: [
        { 
          type: 'walk', 
          name: '步行', 
          time: '点击计算',
          icon: '/static/icons/general/walk.png'
        },
        { 
          type: 'bike', 
          name: '骑行', 
          time: '点击计算',
          icon: '/static/icons/general/bike.png'
        },
        { 
          type: 'bus', 
          name: '公交', 
          time: '点击计算',
          icon: '/static/icons/general/bus.png'
        },
        { 
          type: 'drive', 
          name: '驾车', 
          time: '点击计算',
          icon: '/static/icons/general/car.png'
        }
      ],
      selectedTransport: null,
      // 网友攻略
      strategies: [
        {
          id: 1,
          title: '三日游完美攻略，带你玩转经典景点',
          cover: '/static/images/sightseeing/strategy1.jpg',
          author: '旅行达人小王',
          avatar: '/static/images/avatars/avatar1.jpg',
          likes: 245,
          badgeText: '热门',
          badgeType: 'hot'
        },
        {
          id: 2,
          title: '深度游览指南，发现不一样的美',
          cover: '/static/images/sightseeing/strategy2.jpg',
          author: '历史爱好者',
          avatar: '/static/images/avatars/avatar2.jpg',
          likes: 189,
          badgeText: '精选',
          badgeType: 'featured'
        },
        {
          id: 3,
          title: '胡同里的美食探索，舌尖上的旅行',
          cover: '/static/images/canteen/strategy3.jpg',
          author: '美食探店官',
          avatar: '/static/images/avatars/avatar3.jpg',
          likes: 156,
          badgeText: '新上',
          badgeType: 'new'
        }
      ],
      // 附近推荐
      nearbyPlaces: [
        {
          id: 1,
          name: '老北京炸酱面',
          type: '美食',
          distance: '350m',
          image: '/static/images/food/noodle.jpg'
        },
        {
          id: 2,
          name: '故宫文创店',
          type: '购物',
          distance: '520m',
          image: '/static/images/shopping/nearby2.jpg'
        },
        {
          id: 3,
          name: '景山公园',
          type: '景点',
          distance: '780m',
          image: '/static/images/sightseeing/nearby3.jpg'
        },
        {
          id: 4,
          name: '王府井书店',
          type: '文化',
          distance: '1.2km',
          image: '/static/images/sightseeing/nearby4.jpg'
        }
      ],
      isMapReady: false,
      isMapTouching: false,
      scrollLocked: false,
      isAddingPoint: false,
      pendingPoint: null,
      isCalculatingRoute: false,
      weatherCache: new Map(),
      routeIdFromMyRoutes: null,
      placeCoordinates: {},
      routeCalculationCache: new Map(),
      // 新增：起点终点选择相关数据
      selectedStartIndex: 0,
      selectedEndIndex: 0
    }
  },
  computed: {
    // 新增：当前路线地点列表（用于起点/终点选择器）
    routeOptions() {
      return this.currentRoute.map(point => ({
        name: point.name,
        id: point.id
      }));
    }
  },
  watch: {
    // 监听当前路线变化，自动更新起点/终点默认选择
    currentRoute: {
      handler(newVal) {
        if (newVal.length >= 2) {
          this.selectedStartIndex = 0;
          this.selectedEndIndex = newVal.length - 1;
        }
      },
      immediate: true,
      deep: true
    }
  },
  onLoad(options) {
    console.log('map.vue: 页面加载，参数:', options)
    if (options.routeId) {
      console.log('接收到路线ID:', options.routeId)
      this.routeIdFromMyRoutes = parseInt(options.routeId)
      this.loadRouteById(parseInt(options.routeId))
    } else {
      console.log('未接收到路线ID参数')
    }
    this.calculateHeights();
    this.initMap();
    this.loadUserMarkers();
    this.loadHotStrategies();
    this.checkFirstVisit();
    this.setupEventListeners();
    this.loadSearchHistory();
    this.loadSavedRoutes();
    this.initPlaceCoordinates();
  },
  onShow() {
    if (this.isMapReady) {
      setTimeout(() => {
        this.refreshMap();
        this.loadSavedRoutes();
      }, 300);
    }
  },
  onUnload() {
    this.removeEventListeners();
  },
  onReady() {
    this.mapContext = uni.createMapContext('travelMap', this);
    setTimeout(() => {
      this.isMapReady = true;
      this.refreshMap();
    }, 500);
  },
  methods: {
    // ================== 腾讯地图 Polyline 解码算法（增强兼容性） ==================
    decodeTencentPolyline(encoded) {
      // 如果传入的不是字符串，尝试兼容处理
      if (typeof encoded !== 'string') {
        console.warn('decodeTencentPolyline: 参数不是字符串，返回空数组', encoded);
        return [];
      }
      if (!encoded) return [];
      let points = [];
      let index = 0, lat = 0, lng = 0;
      const len = encoded.length;
      
      while (index < len) {
        let b, shift = 0, result = 0;
        do {
          b = encoded.charCodeAt(index++) - 63;
          result |= (b & 0x1f) << shift;
          shift += 5;
        } while (b >= 0x20);
        const dlat = ((result & 1) ? ~(result >> 1) : (result >> 1));
        lat += dlat;
        
        shift = 0;
        result = 0;
        do {
          b = encoded.charCodeAt(index++) - 63;
          result |= (b & 0x1f) << shift;
          shift += 5;
        } while (b >= 0x20);
        const dlng = ((result & 1) ? ~(result >> 1) : (result >> 1));
        lng += dlng;
        
        points.push({
          latitude: lat / 1e5,
          longitude: lng / 1e5
        });
      }
      return points;
    },

    // ================== 统一路线API请求 ==================
    async requestRouteAPI(url) {
      return new Promise((resolve, reject) => {
        uni.request({
          url: url,
          method: 'GET',
          timeout: 15000,
          success: (res) => {
            if (res.statusCode === 200 && res.data.status === 0) {
              resolve(res.data);
            } else {
              reject(new Error(res.data.message || 'API请求失败'));
            }
          },
          fail: (error) => {
            reject(error);
          }
        });
      });
    },

    // ================== 解析路线响应（增强 polyline 兼容性） ==================
    parseRouteResponse(response, color, transportType) {
      if (!response.result || !response.result.routes || response.result.routes.length === 0) {
        throw new Error('未找到路线');
      }
      const route = response.result.routes[0];
      
      // 解码腾讯地图返回的 polyline 获取实际道路点集（兼容多种格式）
      let polylinePoints = [];
      if (route.polyline) {
        if (typeof route.polyline === 'string') {
          polylinePoints = this.decodeTencentPolyline(route.polyline);
        } else if (Array.isArray(route.polyline)) {
          polylinePoints = route.polyline;
        } else {
          console.warn('未知的 polyline 格式', route.polyline);
          polylinePoints = [];
        }
      } else if (route.polyline_arr && Array.isArray(route.polyline_arr)) {
        polylinePoints = route.polyline_arr.map(point => ({
          latitude: point.latitude,
          longitude: point.longitude
        }));
      }
      
      // 降级方案：使用起点和终点连线
      if (!polylinePoints.length && this.currentRoute.length >= 2) {
        polylinePoints = [
          { latitude: this.currentRoute[0].latitude, longitude: this.currentRoute[0].longitude },
          { latitude: this.currentRoute[this.currentRoute.length - 1].latitude, longitude: this.currentRoute[this.currentRoute.length - 1].longitude }
        ];
      }
      
      // 生成详细的路线步骤
      const steps = this.generateRouteSteps(route, transportType);
      const cost = this.calculateRouteCost(route.distance, transportType);
      
      return {
        polyline: {
          points: polylinePoints,
          color: color,
          width: 6,
          dottedLine: false,
          arrowLine: true
        },
        distance: this.formatDistance(route.distance),
        duration: this.formatDuration(route.duration),
        cost: cost,
        steps: steps
      };
    },

    // ================== 驾车路线规划（支持途经点） ==================
    async calculateDrivingRoute() {
      if (this.currentRoute.length < 2) throw new Error('至少需要两个地点');
      const from = `${this.currentRoute[0].latitude},${this.currentRoute[0].longitude}`;
      const to = `${this.currentRoute[this.currentRoute.length - 1].latitude},${this.currentRoute[this.currentRoute.length - 1].longitude}`;
      let waypoints = '';
      if (this.currentRoute.length > 2) {
        const waypointArray = this.currentRoute.slice(1, -1).map(point => 
          `${point.latitude},${point.longitude}`
        );
        waypoints = `&waypoints=${waypointArray.join(';')}`;
      }
      const url = `${TENCENT_MAP_BASE_URL}/ws/direction/v1/driving/?from=${from}&to=${to}&key=${TENCENT_MAP_KEY}${waypoints}`;
      const response = await this.requestRouteAPI(url);
      return this.parseRouteResponse(response, '#1890ff', 'drive');
    },

    // ================== 步行路线规划（不支持途经点，超过两点时提示） ==================
    async calculateWalkingRoute() {
      if (this.currentRoute.length < 2) throw new Error('至少需要两个地点');
      // 步行不支持途经点，如果超过2个地点，提示用户
      if (this.currentRoute.length > 2) {
        uni.showModal({
          title: '提示',
          content: '步行模式最多支持两个地点之间的路线规划，将为您规划从起点到终点的步行路线。',
          showCancel: false,
          confirmText: '我知道了'
        });
      }
      const from = `${this.currentRoute[0].latitude},${this.currentRoute[0].longitude}`;
      const to = `${this.currentRoute[this.currentRoute.length - 1].latitude},${this.currentRoute[this.currentRoute.length - 1].longitude}`;
      const url = `${TENCENT_MAP_BASE_URL}/ws/direction/v1/walking/?from=${from}&to=${to}&key=${TENCENT_MAP_KEY}`;
      const response = await this.requestRouteAPI(url);
      return this.parseRouteResponse(response, '#52c41a', 'walk');
    },

    // ================== 公交路线规划 ==================
    async calculateTransitRoute() {
      if (this.currentRoute.length < 2) throw new Error('至少需要两个地点');
      const from = `${this.currentRoute[0].latitude},${this.currentRoute[0].longitude}`;
      const to = `${this.currentRoute[this.currentRoute.length - 1].latitude},${this.currentRoute[this.currentRoute.length - 1].longitude}`;
      const url = `${TENCENT_MAP_BASE_URL}/ws/direction/v1/transit/?from=${from}&to=${to}&key=${TENCENT_MAP_KEY}`;
      const response = await this.requestRouteAPI(url);
      return this.parseRouteResponse(response, '#faad14', 'bus');
    },

    // ================== 骑行路线规划（不支持途经点） ==================
    async calculateBicyclingRoute() {
      if (this.currentRoute.length < 2) throw new Error('至少需要两个地点');
      if (this.currentRoute.length > 2) {
        uni.showModal({
          title: '提示',
          content: '骑行模式最多支持两个地点之间的路线规划，将为您规划从起点到终点的骑行路线。',
          showCancel: false,
          confirmText: '我知道了'
        });
      }
      const from = `${this.currentRoute[0].latitude},${this.currentRoute[0].longitude}`;
      const to = `${this.currentRoute[this.currentRoute.length - 1].latitude},${this.currentRoute[this.currentRoute.length - 1].longitude}`;
      const url = `${TENCENT_MAP_BASE_URL}/ws/direction/v1/bicycling/?from=${from}&to=${to}&key=${TENCENT_MAP_KEY}`;
      const response = await this.requestRouteAPI(url);
      return this.parseRouteResponse(response, '#13c2c2', 'bike');
    },

    // ================== 核心路线计算调度 ==================
    async calculateRoute(transportType) {
      if (this.currentRoute.length < 2) {
        uni.showToast({
          title: '至少需要两个地点才能规划路线',
          icon: 'none'
        });
        return;
      }
      if (this.isCalculatingRoute) return;
      this.isCalculatingRoute = true;
      this.updateTransportTime(transportType, '计算中...');
      
      try {
        let routeData = null;
        switch (transportType) {
          case 'drive':
            routeData = await this.calculateDrivingRoute();
            break;
          case 'walk':
            routeData = await this.calculateWalkingRoute();
            break;
          case 'bus':
            routeData = await this.calculateTransitRoute();
            break;
          case 'bike':
            routeData = await this.calculateBicyclingRoute();
            break;
          default:
            routeData = await this.calculateDrivingRoute();
        }
        
        if (routeData && routeData.polyline) {
          // 更新地图路线（替换现有路线）
          this.polylines = [routeData.polyline];
          this.updateTransportTime(transportType, routeData.duration);
          this.routeDetails[transportType] = {
            distance: routeData.distance,
            duration: routeData.duration,
            cost: routeData.cost,
            steps: routeData.steps || []
          };
          
          // 自动调整地图视野以显示完整路线
          if (routeData.polyline.points && routeData.polyline.points.length > 0) {
            setTimeout(() => {
              this.fitRouteBounds(routeData.polyline.points);
            }, 100);
          }
          
          uni.showToast({
            title: `${this.getTransportName(transportType)}路线规划完成`,
            icon: 'success'
          });
        } else {
          throw new Error('路线规划失败');
        }
      } catch (error) {
        console.error('路线规划失败:', error);
        this.updateTransportTime(transportType, '计算失败');
        uni.showToast({
          title: error.message || '路线规划失败，请稍后重试',
          icon: 'none'
        });
      } finally {
        this.isCalculatingRoute = false;
      }
    },

    // ================== 调整地图视野以显示完整路线 ==================
    fitRouteBounds(points) {
      if (!this.mapContext || !points || points.length === 0) return;
      this.mapContext.includePoints({
        points: points,
        padding: [80, 50, 80, 50],
        success: () => {
          console.log('地图视野已调整');
        }
      });
    },

    // ================== 计算路线费用 ==================
    calculateRouteCost(distance, transportType) {
      const distanceKm = distance / 1000;
      let cost = 0;
      switch (transportType) {
        case 'drive':
          cost = (distanceKm / 100) * 8 * 8; // 估算油耗
          break;
        case 'bus':
          cost = 2 + Math.floor(distanceKm / 10);
          break;
        case 'taxi':
          cost = 10 + (distanceKm * 2);
          break;
        default:
          cost = 0;
      }
      return cost > 0 ? `约${cost.toFixed(0)}元` : '免费';
    },

    // ================== 生成路线步骤描述 ==================
    generateRouteSteps(route, transportType) {
      const steps = [];
      if (route.steps && route.steps.length > 0) {
        route.steps.forEach((step, index) => {
          steps.push({
            instruction: step.instruction || `步骤${index + 1}`,
            distance: step.distance ? this.formatDistance(step.distance) : ''
          });
        });
      } else {
        // 备用方案：生成通用步骤
        const stepInstructions = this.getStepInstructionsByTransport(transportType);
        stepInstructions.forEach((instruction, index) => {
          steps.push({
            instruction: instruction,
            distance: index === 2 ? '约500米' : ''
          });
        });
      }
      return steps;
    },

    // ================== 根据交通方式获取步骤模板 ==================
    getStepInstructionsByTransport(transportType) {
      const instructionsMap = {
        'drive': [
          '从起点出发，驶入主路',
          '沿当前道路继续行驶',
          '在下一个路口右转',
          '继续直行约2公里',
          '到达目的地，寻找停车位'
        ],
        'walk': [
          '从起点出发，向北方向前行',
          '在第一个路口右转',
          '沿人行道直行约500米',
          '在十字路口左转',
          '继续前行到达目的地'
        ],
        'bus': [
          '从起点步行至最近公交站',
          '乘坐XX路公交车，经过5站',
          '在XX站下车',
          '步行约300米到达目的地'
        ],
        'bike': [
          '从起点出发，沿自行车道骑行',
          '在第一个路口左转',
          '继续骑行约1公里',
          '注意交通信号灯',
          '到达目的地，停放共享单车'
        ]
      };
      return instructionsMap[transportType] || [
        '从起点出发',
        '沿路线前行',
        '继续前进',
        '接近目的地',
        '到达终点'
      ];
    },

    // ================== 格式化距离 ==================
    formatDistance(distance) {
      if (!distance) return '未知';
      if (distance < 1000) {
        return `${Math.round(distance)}米`;
      } else {
        return `${(distance / 1000).toFixed(1)}公里`;
      }
    },

    // ================== 格式化时间 ==================
    formatDuration(seconds) {
      if (!seconds) return '未知';
      const minutes = Math.ceil(seconds / 60);
      if (minutes < 60) {
        return `${minutes}分钟`;
      } else {
        const hours = Math.floor(minutes / 60);
        const remainingMinutes = minutes % 60;
        return remainingMinutes > 0 ? `${hours}小时${remainingMinutes}分钟` : `${hours}小时`;
      }
    },

    // ================== 更新交通方式的时间显示 ==================
    updateTransportTime(transportType, duration) {
      const option = this.transportOptions.find(opt => opt.type === transportType);
      if (option) {
        option.time = duration;
      }
    },

    // ================== 获取交通方式名称 ==================
    getTransportName(type) {
      const nameMap = {
        'walk': '步行',
        'bike': '骑行',
        'bus': '公交',
        'drive': '驾车'
      };
      return nameMap[type] || '步行';
    },

    // ================== 选择交通方式 ==================
    selectTransport(type) {
      this.selectedTransport = type;
      this.calculateRoute(type);
    },

    // ================== 重置交通时间显示 ==================
    resetTransportTimes() {
      this.transportOptions.forEach(option => {
        option.time = '点击计算';
      });
      this.selectedTransport = null;
      this.routeDetails = {
        walk: null,
        bike: null,
        bus: null,
        drive: null
      };
      this.polylines = [];
    },

    // ================== 以下为原有方法（保持不变） ==================
    initPlaceCoordinates() {
      this.placeCoordinates = {
        '故宫': { latitude: 39.916, longitude: 116.397 },
        '天安门': { latitude: 39.909, longitude: 116.397 },
        '颐和园': { latitude: 39.999, longitude: 116.273 },
        '长城': { latitude: 40.356, longitude: 116.020 },
        '王府井': { latitude: 39.914, longitude: 116.417 },
        '南锣鼓巷': { latitude: 39.939, longitude: 116.404 },
        '鸟巢': { latitude: 39.993, longitude: 116.396 },
        '水立方': { latitude: 39.991, longitude: 116.387 },
        '天坛': { latitude: 39.883, longitude: 116.407 },
        '圆明园': { latitude: 40.008, longitude: 116.297 },
        '外滩': { latitude: 31.233, longitude: 121.483 },
        '东方明珠': { latitude: 31.240, longitude: 121.505 },
        '南京路': { latitude: 31.238, longitude: 121.475 },
        '豫园': { latitude: 31.227, longitude: 121.487 },
        '上海迪士尼': { latitude: 31.144, longitude: 121.658 },
        '陆家嘴': { latitude: 31.239, longitude: 121.500 },
        '田子坊': { latitude: 31.207, longitude: 121.464 },
        '广州塔': { latitude: 23.119, longitude: 113.323 },
        '白云山': { latitude: 23.181, longitude: 113.297 },
        '珠江夜游': { latitude: 23.107, longitude: 113.325 },
        '北京路': { latitude: 23.124, longitude: 113.267 },
        '上下九': { latitude: 23.116, longitude: 113.248 },
        '沙面': { latitude: 23.107, longitude: 113.243 },
        '世界之窗': { latitude: 22.537, longitude: 113.971 },
        '欢乐谷': { latitude: 22.541, longitude: 113.980 },
        '东部华侨城': { latitude: 22.631, longitude: 114.295 },
        '深圳湾公园': { latitude: 22.495, longitude: 113.946 },
        '华强北': { latitude: 22.544, longitude: 114.085 },
        '宽窄巷子': { latitude: 30.663, longitude: 104.055 },
        '锦里': { latitude: 30.645, longitude: 104.048 },
        '武侯祠': { latitude: 30.646, longitude: 104.047 },
        '杜甫草堂': { latitude: 30.661, longitude: 104.026 },
        '春熙路': { latitude: 30.657, longitude: 104.080 },
        '太古里': { latitude: 30.659, longitude: 104.084 },
        '熊猫基地': { latitude: 30.735, longitude: 104.143 },
        '都江堰': { latitude: 31.008, longitude: 103.607 },
        '青城山': { latitude: 30.901, longitude: 103.568 },
        '兵马俑': { latitude: 34.385, longitude: 109.273 },
        '大雁塔': { latitude: 34.219, longitude: 108.962 },
        '钟楼': { latitude: 34.261, longitude: 108.943 },
        '回民街': { latitude: 34.264, longitude: 108.940 },
        '华清池': { latitude: 34.361, longitude: 109.214 },
        '城墙': { latitude: 34.260, longitude: 108.944 },
        '西湖': { latitude: 30.247, longitude: 120.147 },
        '雷峰塔': { latitude: 30.229, longitude: 120.149 },
        '灵隐寺': { latitude: 30.237, longitude: 120.096 },
        '宋城': { latitude: 30.174, longitude: 120.091 },
        '河坊街': { latitude: 30.238, longitude: 120.168 },
        '断桥残雪': { latitude: 30.257, longitude: 120.144 },
        '苏堤春晓': { latitude: 30.245, longitude: 120.138 },
        '三潭印月': { latitude: 30.239, longitude: 120.142 },
        '中山陵': { latitude: 32.061, longitude: 118.853 },
        '夫子庙': { latitude: 32.023, longitude: 118.790 },
        '玄武湖': { latitude: 32.074, longitude: 118.797 },
        '总统府': { latitude: 32.045, longitude: 118.797 },
        '南京博物院': { latitude: 32.042, longitude: 118.827 },
        '洪崖洞': { latitude: 29.563, longitude: 106.583 },
        '解放碑': { latitude: 29.558, longitude: 106.575 },
        '磁器口': { latitude: 29.579, longitude: 106.449 },
        '长江索道': { latitude: 29.556, longitude: 106.582 },
        '武隆天生三桥': { latitude: 29.432, longitude: 107.793 },
        '黄鹤楼': { latitude: 30.547, longitude: 114.299 },
        '东湖': { latitude: 30.556, longitude: 114.367 },
        '户部巷': { latitude: 30.549, longitude: 114.299 },
        '武汉大学': { latitude: 30.538, longitude: 114.368 },
        '江汉路': { latitude: 30.580, longitude: 114.293 },
        '鼓浪屿': { latitude: 24.448, longitude: 118.067 },
        '厦门大学': { latitude: 24.438, longitude: 118.097 },
        '曾厝垵': { latitude: 24.434, longitude: 118.124 },
        '环岛路': { latitude: 24.443, longitude: 118.176 },
        '南普陀寺': { latitude: 24.441, longitude: 118.094 },
        '栈桥': { latitude: 36.061, longitude: 120.319 },
        '八大关': { latitude: 36.053, longitude: 120.346 },
        '崂山': { latitude: 36.208, longitude: 120.591 },
        '五四广场': { latitude: 36.066, longitude: 120.383 },
        '啤酒博物馆': { latitude: 36.078, longitude: 120.348 },
        '星海广场': { latitude: 38.887, longitude: 121.602 },
        '老虎滩': { latitude: 38.878, longitude: 121.679 },
        '金石滩': { latitude: 39.088, longitude: 122.008 },
        '发现王国': { latitude: 39.087, longitude: 122.006 },
        '滨海路': { latitude: 38.880, longitude: 121.645 },
        '亚龙湾': { latitude: 18.239, longitude: 109.632 },
        '天涯海角': { latitude: 18.299, longitude: 109.348 },
        '蜈支洲岛': { latitude: 18.317, longitude: 109.763 },
        '南山寺': { latitude: 18.297, longitude: 109.204 },
        '大东海': { latitude: 18.222, longitude: 109.523 },
        '石林': { latitude: 24.820, longitude: 103.337 },
        '滇池': { latitude: 24.839, longitude: 102.658 },
        '西山': { latitude: 24.958, longitude: 102.625 },
        '翠湖公园': { latitude: 25.047, longitude: 102.704 },
        '云南民族村': { latitude: 24.961, longitude: 102.645 },
        '大理古城': { latitude: 25.689, longitude: 100.165 },
        '丽江古城': { latitude: 26.876, longitude: 100.232 },
        '玉龙雪山': { latitude: 27.098, longitude: 100.178 },
        '洱海': { latitude: 25.794, longitude: 100.186 },
        '西双版纳': { latitude: 22.007, longitude: 100.798 },
        '漓江': { latitude: 25.234, longitude: 110.480 },
        '象鼻山': { latitude: 25.268, longitude: 110.294 },
        '阳朔西街': { latitude: 24.778, longitude: 110.496 },
        '龙脊梯田': { latitude: 25.758, longitude: 110.152 },
        '七星公园': { latitude: 25.271, longitude: 110.305 },
        '拙政园': { latitude: 31.323, longitude: 120.626 },
        '狮子林': { latitude: 31.324, longitude: 120.629 },
        '虎丘': { latitude: 31.339, longitude: 120.573 },
        '周庄': { latitude: 31.116, longitude: 120.846 },
        '平江路': { latitude: 31.319, longitude: 120.634 },
        '珠海长隆': { latitude: 22.133, longitude: 113.549 },
        '情侣路': { latitude: 22.277, longitude: 113.577 },
        '珠海渔女': { latitude: 22.281, longitude: 113.577 },
        '圆明新园': { latitude: 22.252, longitude: 113.547 },
        '横琴岛': { latitude: 22.117, longitude: 113.549 },
        '火车站': { latitude: 39.902, longitude: 116.427 },
        '机场': { latitude: 40.080, longitude: 116.585 },
        '汽车站': { latitude: 39.883, longitude: 116.387 },
        '医院': { latitude: 39.904, longitude: 116.407 },
        '学校': { latitude: 39.909, longitude: 116.397 },
        '商场': { latitude: 39.914, longitude: 116.470 },
        '超市': { latitude: 39.908, longitude: 116.468 },
        '公园': { latitude: 39.917, longitude: 116.415 },
        '餐厅': { latitude: 39.906, longitude: 116.397 },
        '酒店': { latitude: 39.904, longitude: 116.407 }
      };
    },
    
    setupEventListeners() {
      uni.$on('routesUpdated', this.handleRoutesUpdated);
      uni.$on('loadRouteOnMap', this.handleLoadRouteOnMap);
    },
    
    removeEventListeners() {
      uni.$off('routesUpdated', this.handleRoutesUpdated);
      uni.$off('loadRouteOnMap', this.handleLoadRouteOnMap);
    },
    
    handleRoutesUpdated() {
      console.log('收到行程规划更新事件，重新加载数据');
      this.loadSavedRoutes();
    },
    
    handleLoadRouteOnMap(routeId) {
      console.log('收到加载行程事件，routeId:', routeId);
      this.loadRouteById(routeId);
    },
    
    loadRouteById(routeId) {
      const savedRoutes = uni.getStorageSync('user_routes') || [];
      const route = savedRoutes.find(r => r.id === routeId);
      if (route) {
        this.selectSavedRoute(route);
      } else {
        uni.showToast({
          title: '行程规划不存在',
          icon: 'none'
        });
        this.loadSavedRoutes();
      }
    },
    
    calculateHeights() {
      try {
        const systemInfo = uni.getSystemInfoSync();
        const windowHeight = systemInfo.windowHeight;
        this.mapHeight = windowHeight * 0.5;
      } catch (error) {
        console.error('获取系统信息失败:', error);
        this.mapHeight = 400;
      }
    },
    
    initMap() {
      console.log('初始化地图...');
      this.getCurrentLocation();
    },
    
    loadSearchHistory() {
      try {
        const history = uni.getStorageSync('search_history') || [];
        this.searchHistory = history;
      } catch (error) {
        console.error('加载搜索历史失败:', error);
        this.searchHistory = [];
      }
    },
    
    saveSearchHistory(keyword) {
      if (!keyword.trim()) return;
      const history = this.searchHistory.filter(item => item !== keyword);
      history.unshift(keyword);
      this.searchHistory = history.slice(0, 10);
      try {
        uni.setStorageSync('search_history', this.searchHistory);
      } catch (error) {
        console.error('保存搜索历史失败:', error);
      }
    },
    
    clearSearchHistory() {
      uni.showModal({
        title: '清除搜索历史',
        content: '确定要清除所有搜索历史吗？',
        confirmColor: '#ff6b6b',
        success: (res) => {
          if (res.confirm) {
            this.searchHistory = [];
            try {
              uni.setStorageSync('search_history', []);
            } catch (error) {
              console.error('清除搜索历史失败:', error);
            }
          }
        }
      });
    },
    
    searchFromHistory(keyword) {
      this.searchKeyword = keyword;
      this.doSearch();
    },
    
    searchFromHot(keyword) {
      this.searchKeyword = keyword;
      this.doSearch();
    },
    
    onSearchFocus() {
      this.showSearchPage = true;
    },
    
    hideSearchPage() {
      this.showSearchPage = false;
      this.showSearchResults = false;
      this.searchKeyword = '';
    },
    
    onSearchInput(e) {
      this.searchKeyword = e.detail.value;
      if (this.searchKeyword.trim()) {
        this.debounceSearch();
      } else {
        this.showSearchResults = false;
        this.searchResults = [];
      }
    },
    
    debounceSearch() {
      if (this.searchTimer) {
        clearTimeout(this.searchTimer);
      }
      this.searchTimer = setTimeout(() => {
        this.doSearch();
      }, 500);
    },
    
    onSearchConfirm() {
      if (this.searchKeyword.trim()) {
        this.doSearch();
      }
    },
    
    async doSearch() {
      const keyword = this.searchKeyword.trim();
      if (!keyword) {
        uni.showToast({
          title: '请输入搜索关键词',
          icon: 'none'
        });
        return;
      }
      this.isSearching = true;
      this.showSearchResults = true;
      uni.showLoading({
        title: '搜索中...'
      });
      try {
        const results = await this.searchPlaces(keyword);
        this.searchResults = results;
        this.saveSearchHistory(keyword);
        if (results.length === 0) {
          uni.showToast({
            title: '未找到相关地点',
            icon: 'none'
          });
        }
      } catch (error) {
        console.error('搜索失败:', error);
        uni.showToast({
          title: '搜索失败，请重试',
          icon: 'none'
        });
        this.searchResults = [];
      } finally {
        this.isSearching = false;
        uni.hideLoading();
      }
    },
    
    clearSearch() {
      this.searchKeyword = '';
      this.showSearchResults = false;
      this.searchResults = [];
    },
    
    hideSearchResults() {
      this.showSearchResults = false;
      this.searchResults = [];
    },
    
    async searchPlaces(keyword, region = '全国') {
      try {
        const url = `${TENCENT_MAP_BASE_URL}/ws/place/v1/suggestion/?region=${encodeURIComponent(region)}&keyword=${encodeURIComponent(keyword)}&key=${TENCENT_MAP_KEY}`;
        console.log('搜索请求URL:', url);
        const response = await new Promise((resolve, reject) => {
          uni.request({
            url: url,
            method: 'GET',
            timeout: 10000,
            success: (res) => {
              console.log('搜索API响应:', res);
              if (res.statusCode === 200 && res.data.status === 0) {
                resolve(res.data);
              } else {
                reject(new Error(res.data.message || '搜索失败'));
              }
            },
            fail: (error) => {
              reject(error);
            }
          });
        });
        if (response.status === 0 && response.data) {
          return response.data.map(item => ({
            id: item.id,
            title: item.title,
            address: item.address,
            province: item.province,
            city: item.city,
            district: item.district,
            latitude: parseFloat(item.location.lat),
            longitude: parseFloat(item.location.lng),
            type: item.type || 'poi',
            category: item.category || '一般地点',
            distance: item._distance ? this.formatDistance(item._distance) : ''
          }));
        } else {
          throw new Error(response.message || '搜索无结果');
        }
      } catch (error) {
        console.error('腾讯地图搜索失败:', error);
        throw error;
      }
    },
    
    async selectSearchResult(place) {
      console.log('选择地点:', place);
      this.hideSearchPage();
      this.moveMapToLocation(place.latitude, place.longitude, place.title);
      this.addSearchResultMarker(place);
      const temperature = await this.getTemperatureForLocation(place.latitude, place.longitude);
      this.askAddToRoute(place, temperature);
    },
    
    moveMapToLocation(latitude, longitude, title) {
      this.mapCenter.latitude = latitude;
      this.mapCenter.longitude = longitude;
      this.mapScale = 16;
      if (this.mapContext) {
        this.mapContext.moveToLocation({
          latitude: latitude,
          longitude: longitude,
          success: () => {
            console.log(`地图已移动到: ${title}`);
          },
          fail: (error) => {
            console.error('移动地图失败:', error);
          }
        });
      }
      this.$nextTick(() => {
        this.refreshMap();
      });
    },
    
    addSearchResultMarker(place) {
      this.markers = this.markers.filter(marker => 
        marker.id === 0 || this.currentRoute.some(point => point.id === marker.id)
      );
      const markerId = 'search_' + Date.now();
      this.markers.push({
        id: markerId,
        latitude: place.latitude,
        longitude: place.longitude,
        title: place.title,
        width: 40,
        height: 40,
        callout: {
          content: `${place.title}\n${place.address}`,
          color: '#333',
          fontSize: 12,
          borderRadius: 10,
          bgColor: '#FFFFFF',
          padding: 10,
          display: 'ALWAYS'
        }
      });
      console.log('已添加搜索结果标记:', markerId);
    },
    
    // 检查是否重复（名称或坐标）
    isPointDuplicate(name, latitude, longitude, tolerance = 0.0001) {
      return this.currentRoute.some(point => {
        // 名称完全相同
        if (point.name === name) return true;
        // 坐标距离小于容差
        const latDiff = Math.abs(point.latitude - latitude);
        const lngDiff = Math.abs(point.longitude - longitude);
        return latDiff < tolerance && lngDiff < tolerance;
      });
    },
    
    askAddToRoute(place, temperature) {
      // 防重复
      if (this.isPointDuplicate(place.title, place.latitude, place.longitude)) {
        uni.showToast({
          title: '该地点已在路线中',
          icon: 'none'
        });
        return;
      }
      uni.showModal({
        title: '添加到路线',
        content: `是否将"${place.title}"添加到路线中？\n当前天气: ${temperature}`,
        confirmText: '添加',
        cancelText: '仅查看',
        success: (res) => {
          if (res.confirm) {
            this.addPointToRoute({
              name: place.title,
              latitude: place.latitude,
              longitude: place.longitude,
              type: 'search',
              address: place.address,
              fromSearch: true,
              temperature: temperature
            });
          }
        }
      });
    },
    
    loadSavedRoutes() {
      try {
        const savedRoutes = uni.getStorageSync('user_routes') || [];
        this.savedRoutes = savedRoutes;
        console.log('加载行程规划:', this.savedRoutes.length, '条');
        if (this.selectedRouteId && !savedRoutes.find(r => r.id === this.selectedRouteId)) {
          this.selectedRouteId = null;
        }
      } catch (error) {
        console.error('加载行程规划失败:', error);
        this.savedRoutes = [];
      }
    },
    
    async selectSavedRoute(route) {
      this.selectedRouteId = route.id;
      this.markers = this.markers.filter(marker => marker.id === 0);
      this.currentRoute = [];
      this.polylines = [];
      this.resetTransportTimes();
      
      if (route.places && route.places.length > 0) {
        for (let i = 0; i < route.places.length; i++) {
          const placeName = route.places[i];
          let coordinates = this.placeCoordinates[placeName];
          if (!coordinates) {
            coordinates = {
              latitude: this.mapCenter.latitude + (i * 0.01),
              longitude: this.mapCenter.longitude + (i * 0.01)
            };
          }
          const temperature = await this.getTemperatureForLocation(coordinates.latitude, coordinates.longitude);
          const point = {
            id: route.id * 1000 + i,
            name: placeName,
            latitude: coordinates.latitude,
            longitude: coordinates.longitude,
            temperature: temperature,
            visitors: '行程规划地点',
            type: 'attraction'
          };
          this.currentRoute.push(point);
          this.markers.push({
            id: point.id,
            latitude: point.latitude,
            longitude: point.longitude,
            title: point.name,
            iconPath: this.getMarkerIcon(point.type),
            width: 36,
            height: 36,
            callout: {
              content: `${point.name}\n${point.temperature}`,
              color: '#333',
              fontSize: 12,
              borderRadius: 10,
              bgColor: '#FFFFFF',
              padding: 10,
              display: 'ALWAYS'
            }
          });
        }
        this.focusOnRoute();
        uni.showToast({
          title: `已加载行程：${route.name}`,
          icon: 'success'
        });
      }
    },
    
    getPlaceCoordinates(places) {
      return places.map(place => {
        if (this.placeCoordinates[place]) {
          return this.placeCoordinates[place];
        }
        const randomLat = (Math.random() - 0.5) * 0.1;
        const randomLng = (Math.random() - 0.5) * 0.1;
        return {
          latitude: this.mapCenter.latitude + randomLat,
          longitude: this.mapCenter.longitude + randomLng
        };
      });
    },
    
    focusOnRoute() {
      if (this.currentRoute.length === 0) return;
      if (this.mapContext) {
        const points = this.currentRoute.map(point => ({
          latitude: point.latitude,
          longitude: point.longitude
        }));
        this.mapContext.includePoints({
          points: points,
          padding: [50, 50, 50, 50]
        });
      }
      this.mapScale = 12;
      this.refreshMap();
    },
    
    focusOnPoint(point, index) {
      this.activeRouteIndex = index;
      this.mapCenter.latitude = point.latitude;
      this.mapCenter.longitude = point.longitude;
      this.mapScale = 16;
      if (this.mapContext) {
        this.mapContext.moveToLocation({
          latitude: point.latitude,
          longitude: point.longitude
        });
      }
      this.refreshMap();
      console.log(`聚焦到地点: ${point.name}, 索引: ${index}`);
    },
    
    viewRouteDetail(routeId) {
      uni.navigateTo({
        url: `/pages/route-detail/route-detail?id=${routeId}`
      });
    },
    
    deleteSavedRoute(routeId) {
      uni.showModal({
        title: '删除行程规划',
        content: '确定要删除这个行程规划吗？',
        confirmColor: '#ff6b6b',
        success: (res) => {
          if (res.confirm) {
            try {
              const savedRoutes = uni.getStorageSync('user_routes') || [];
              const updatedRoutes = savedRoutes.filter(route => route.id !== routeId);
              uni.setStorageSync('user_routes', updatedRoutes);
              this.savedRoutes = updatedRoutes;
              if (this.selectedRouteId === routeId) {
                this.selectedRouteId = null;
                this.clearRoute();
              }
              uni.$emit('routesUpdated');
              uni.showToast({
                title: '删除成功',
                icon: 'success'
              });
            } catch (error) {
              console.error('删除行程规划失败:', error);
              uni.showToast({
                title: '删除失败',
                icon: 'none'
              });
            }
          }
        }
      });
    },
    
    goToMyRoutes() {
      uni.navigateTo({
        url: '/pages/my-routes/my-routes'
      });
    },
    
    async getCurrentLocation() {
      this.locationStatus = '定位中...';
      uni.showLoading({
        title: '定位中...',
        mask: true
      });
      try {
        const preciseResult = await this.tryUniGetLocation();
        if (preciseResult.success) {
          console.log('uni.getLocation成功:', preciseResult);
          this.handleLocationSuccess(preciseResult.latitude, preciseResult.longitude, '精确定位');
          return;
        }
        console.log('尝试使用腾讯地图IP定位...');
        this.locationStatus = '使用IP定位...';
        const ipResult = await this.tryTencentIPLocation();
        if (ipResult.success) {
          console.log('腾讯地图IP定位成功:', ipResult);
          this.handleLocationSuccess(ipResult.latitude, ipResult.longitude, 'IP定位');
          return;
        }
        console.log('所有定位方法都失败，使用默认位置（北京）');
        this.useDefaultLocation('定位失败，使用默认位置（北京）');
      } catch (error) {
        console.error('定位过程中发生错误:', error);
        this.useDefaultLocation('定位异常，使用默认位置（北京）');
      } finally {
        uni.hideLoading();
      }
    },
    
    tryUniGetLocation() {
      return new Promise((resolve) => {
        uni.getLocation({
          type: 'gcj02',
          altitude: true,
          isHighAccuracy: true,
          highAccuracyExpireTime: 5000,
          success: (res) => {
            console.log('uni.getLocation成功:', res);
            resolve({
              success: true,
              latitude: res.latitude,
              longitude: res.longitude,
              source: 'uni.getLocation'
            });
          },
          fail: (error) => {
            console.log('uni.getLocation失败:', error);
            if (error.errMsg && (error.errMsg.includes('auth deny') || error.errMsg.includes('permission'))) {
              this.showPermissionModal = true;
            }
            resolve({ success: false, error: error });
          }
        });
      });
    },
    
    async tryTencentIPLocation() {
      try {
        const url = `${TENCENT_MAP_BASE_URL}/ws/location/v1/ip?key=${TENCENT_MAP_KEY}&output=json`;
        console.log('请求腾讯地图IP定位API:', url);
        const response = await new Promise((resolve, reject) => {
          uni.request({
            url: url,
            method: 'GET',
            timeout: 10000,
            success: (res) => {
              console.log('腾讯地图API响应:', res);
              if (res.statusCode === 200 && res.data.status === 0) {
                resolve(res.data);
              } else {
                reject(new Error(`API返回错误: ${res.data.message || '未知错误'}`));
              }
            },
            fail: (error) => {
              reject(error);
            }
          });
        });
        if (response.status === 0 && response.result) {
          const location = response.result.location;
          return {
            success: true,
            latitude: location.lat,
            longitude: location.lng,
            source: 'Tencent IP Location'
          };
        } else {
          throw new Error(response.message || '腾讯地图IP定位失败');
        }
      } catch (error) {
        console.error('腾讯地图IP定位失败:', error);
        return { success: false, error: error };
      }
    },
    
    handleLocationSuccess(latitude, longitude, source) {
      console.log(`${source}成功:`, latitude, longitude);
      this.mapCenter.latitude = latitude;
      this.mapCenter.longitude = longitude;
      this.addCurrentLocationMarker(latitude, longitude);
      this.$nextTick(() => {
        this.refreshMap();
      });
      this.locationStatus = `${source}成功`;
      setTimeout(() => {
        this.locationStatus = '';
      }, 2000);
      uni.showToast({
        title: `${source}成功`,
        icon: 'success',
        duration: 1500
      });
    },
    
    useDefaultLocation(reason) {
      console.log(reason);
      this.mapCenter.latitude = 39.916;
      this.mapCenter.longitude = 116.397;
      this.addCurrentLocationMarker(this.mapCenter.latitude, this.mapCenter.longitude);
      this.$nextTick(() => {
        this.refreshMap();
      });
      this.locationStatus = reason;
      setTimeout(() => {
        this.locationStatus = '';
      }, 2000);
      if (reason) {
        uni.showToast({
          title: reason,
          icon: 'none',
          duration: 2000
        });
      }
    },
    
    addCurrentLocationMarker(latitude, longitude) {
      this.markers = this.markers.filter(marker => marker.id !== 0);
      this.markers.push({
        id: 0,
        latitude: latitude,
        longitude: longitude,
        title: '我的位置',
        width: 40,
        height: 40,
        zIndex: 999,
        callout: {
          content: '我的位置',
          color: '#333',
          fontSize: 14,
          borderRadius: 12,
          bgColor: '#FFFFFF',
          padding: 10,
          display: 'ALWAYS'
        }
      });
    },
    
    requestLocationPermission() {
      this.hidePermissionModal();
      uni.openSetting({
        success: (res) => {
          console.log('打开设置页面:', res);
          if (res.authSetting['scope.userLocation']) {
            uni.showToast({
              title: '权限已开启，重新定位中',
              icon: 'success'
            });
            setTimeout(() => {
              this.getCurrentLocation();
            }, 1000);
          }
        },
        fail: (err) => {
          console.log('打开设置页面失败:', err);
          uni.showToast({
            title: '打开设置失败',
            icon: 'none'
          });
        }
      });
    },
    
    hidePermissionModal() {
      this.showPermissionModal = false;
    },
    
    async getAddressByLocation(latitude, longitude) {
      try {
        const url = `${TENCENT_MAP_BASE_URL}/ws/geocoder/v1/?key=${TENCENT_MAP_KEY}&location=${latitude},${longitude}`;
        const response = await new Promise((resolve, reject) => {
          uni.request({
            url: url,
            method: 'GET',
            timeout: 10000,
            success: (res) => {
              if (res.statusCode === 200 && res.data.status === 0) {
                resolve(res.data);
              } else {
                reject(new Error(res.data.message || '逆地理编码失败'));
              }
            },
            fail: (err) => {
              reject(err);
            }
          });
        });
        return response.result;
      } catch (error) {
        console.error('腾讯地图逆地理编码失败:', error);
        return null;
      }
    },
    
    async loadUserMarkers() {
      this.markers = this.markers.filter(marker => marker.id === 0);
      const userMarkers = [
        { id: 1, name: '故宫', latitude: 39.916, longitude: 116.397, type: 'attraction' },
        { id: 2, name: '天安门', latitude: 39.909, longitude: 116.397, type: 'attraction' },
        { id: 3, name: '王府井', latitude: 39.914, longitude: 116.417, type: 'shopping' }
      ];
      for (let marker of userMarkers) {
        const temperature = await this.getTemperatureForLocation(marker.latitude, marker.longitude);
        const visitors = `${Math.floor(Math.random() * 1000) + 1000}人在附近`;
        const existingMarker = this.markers.find(m => m.id === marker.id);
        if (!existingMarker) {
          this.markers.push({
            id: marker.id,
            latitude: marker.latitude,
            longitude: marker.longitude,
            title: marker.name,
            iconPath: this.getMarkerIcon(marker.type),
            width: 36,
            height: 36,
            callout: {
              content: `${marker.name}\n${temperature}`,
              color: '#333',
              fontSize: 12,
              borderRadius: 10,
              bgColor: '#FFFFFF',
              padding: 10,
              display: 'ALWAYS'
            }
          });
        }
        // 避免重复添加默认地点到当前路线（如果已经存在相同名称）
        if (!this.selectedRouteId && !this.isPointDuplicate(marker.name, marker.latitude, marker.longitude)) {
          this.currentRoute.push({
            ...marker,
            temperature: temperature,
            visitors: visitors
          });
        }
      }
      this.$nextTick(() => {
        this.refreshMap();
      });
    },
    
    getMarkerIcon(type) {
      const iconMap = {
        'attraction': '/static/icons/general/attraction.png',
        'hotel': '/static/icons/general/hotel.png',
        'shopping': '/static/icons/general/shopping.png',
        'food': '/static/icons/general/food.png',
        'search': '/static/icons/general/search.png',
        'default': '/static/icons/general/default.png'
      };
      return iconMap[type] || '/static/icons/general/default.png';
    },
    
    refreshMap() {
      if (this.mapContext && this.isMapReady) {
        this.mapContext.moveToLocation({
          latitude: this.mapCenter.latitude,
          longitude: this.mapCenter.longitude,
          complete: () => {
            console.log('地图刷新完成');
          }
        });
      }
    },
    
    onFunctionButtonTap(item) {
      switch (item.type) {
        case 'gas':
          uni.navigateTo({ url: '/pages/gas-station/gas-station' });
          break;
        case 'hotel':
          uni.navigateTo({ url: '/pages/hotel/hotel' });
          break;
        case 'food':
          uni.navigateTo({ url: '/pages/food/food' });
          break;
        case 'shopping':
          uni.navigateTo({ url: '/pages/shopping/shopping' });
          break;
        case 'ticket':
          uni.navigateTo({ url: '/pages/ticket/ticket' });
          break;
        case 'bus':
          uni.navigateTo({ url: '/pages/bus/bus' });
          break;
        case 'taxi':
          uni.navigateTo({ url: '/pages/taxi/taxi' });
          break;
        case 'route':
          uni.navigateTo({ url: '/pages/route/route' });
          break;
        case 'bike':
          uni.navigateTo({ url: '/pages/bike/bike' });
          break;
        case 'realtime-bus':
          uni.navigateTo({ url: '/pages/realtime-bus/realtime-bus' });
          break;
      }
    },
    
    onRegionChange(e) {
      if (e.type === 'end') {
        console.log('地图区域变化', e);
      }
    },
    
    onMarkerTap(e) {
      const markerId = e.markerId;
      const marker = this.markers.find(m => m.id === markerId);
      if (marker) {
        const index = this.currentRoute.findIndex(item => item.id === markerId);
        if (index !== -1) {
          this.focusOnPoint(marker, index);
        }
      }
    },
    
    onCalloutTap(e) {
      const markerId = e.markerId;
      const marker = this.markers.find(m => m.id === markerId);
      if (marker) {
        this.goToWeather(marker);
      }
    },
    
    onMapTap(e) {
      if (!this.isAddingPoint) return;
      const { latitude, longitude } = e.detail;
      console.log('地图点击坐标:', latitude, longitude);
      uni.showLoading({
        title: '获取位置信息...'
      });
      this.getAddressByLocation(latitude, longitude).then(addressInfo => {
        uni.hideLoading();
        if (addressInfo) {
          const address = addressInfo.address_component;
          const locationName = addressInfo.address || 
                               `${address.province}${address.city}${address.district}${address.street}${address.street_number}`;
          this.showAddPointConfirm(latitude, longitude, locationName);
        } else {
          uni.showToast({
            title: '获取位置信息失败',
            icon: 'none'
          });
        }
      }).catch(error => {
        uni.hideLoading();
        uni.showToast({
          title: '获取位置信息失败',
          icon: 'none'
        });
        console.error('逆地理编码失败:', error);
      });
    },
    
    async showAddPointConfirm(latitude, longitude, locationName) {
      // 防止重复添加
      if (this.isPointDuplicate(locationName, latitude, longitude)) {
        uni.showToast({
          title: '该地点已在路线中',
          icon: 'none'
        });
        return;
      }
      const temperature = await this.getTemperatureForLocation(latitude, longitude);
      uni.showModal({
        title: '添加地点',
        content: `确定要添加"${locationName}"到路线吗？\n当前天气: ${temperature}`,
        confirmText: '添加',
        cancelText: '取消',
        success: (res) => {
          if (res.confirm) {
            this.addPointToRoute({
              name: locationName,
              latitude: latitude,
              longitude: longitude,
              type: 'custom',
              temperature: temperature
            });
          }
        }
      });
    },
    
    onScroll(e) {
      this.scrollTop = e.detail.scrollTop;
    },
    
    zoomIn() {
      this.mapScale = Math.min(this.mapScale + 1, 18);
      this.refreshMap();
    },
    
    zoomOut() {
      this.mapScale = Math.max(this.mapScale - 1, 3);
      this.refreshMap();
    },
    
    locateMe() {
      this.getCurrentLocation();
    },
    
    showRouteOptions() {
      const options = ['添加新地点', '点击地图添加地点'];
      if (this.currentRoute.length > 0) {
        options.push('重新规划路线');
      }
      uni.showActionSheet({
        itemList: options,
        success: (res) => {
          switch (res.tapIndex) {
            case 0:
              this.addNewPoint();
              break;
            case 1:
              this.enableMapPointAdding();
              break;
            case 2:
              if (this.currentRoute.length > 0) {
                this.replanRoute();
              }
              break;
          }
        },
        fail: () => {
          console.log('用户取消操作');
        }
      });
    },
    
    enableMapPointAdding() {
      this.isAddingPoint = true;
      uni.showToast({
        title: '请点击地图选择位置',
        icon: 'none',
        duration: 2000
      });
      setTimeout(() => {
        if (this.isAddingPoint) {
          this.isAddingPoint = false;
          uni.showToast({
            title: '添加地点模式已关闭',
            icon: 'none',
            duration: 1500
          });
        }
      }, 3000);
    },
    
    addNewPoint() {
      this.onSearchFocus();
    },
    
    async addPointToRoute(locationData) {
      if (!locationData || !locationData.name || !locationData.latitude || !locationData.longitude) {
        uni.showToast({
          title: '地点信息不完整，无法添加',
          icon: 'none'
        });
        return;
      }
      // 再次检查重复（双重保险）
      if (this.isPointDuplicate(locationData.name, locationData.latitude, locationData.longitude)) {
        uni.showToast({
          title: '该地点已在路线中',
          icon: 'none'
        });
        return;
      }
      let temperatureText = locationData.temperature;
      if (!temperatureText) {
        temperatureText = await this.getTemperatureForLocation(locationData.latitude, locationData.longitude);
      }
      const newPoint = {
        id: Date.now(),
        name: locationData.name,
        latitude: locationData.latitude,
        longitude: locationData.longitude,
        temperature: temperatureText,
        visitors: '新添加的地点',
        type: locationData.type || 'default'
      };
      this.markers.push({
        id: newPoint.id,
        latitude: newPoint.latitude,
        longitude: newPoint.longitude,
        title: newPoint.name,
        iconPath: this.getMarkerIcon(newPoint.type),
        width: 36,
        height: 36,
        callout: {
          content: `${newPoint.name}\n${newPoint.temperature}`,
          color: '#333',
          fontSize: 12,
          borderRadius: 10,
          bgColor: '#FFFFFF',
          padding: 10,
          display: 'ALWAYS'
        }
      });
      this.currentRoute.push(newPoint);
      // 添加地点后重置路线显示
      this.resetTransportTimes();
      this.polylines = [];
      if (locationData.fromSearch) {
        this.moveMapToLocation(locationData.latitude, locationData.longitude, locationData.name);
      }
      this.refreshMap();
      this.isAddingPoint = false;
      uni.showToast({
        title: '地点添加成功',
        icon: 'success'
      });
    },
    
    removePoint(index) {
      if (this.currentRoute.length <= 1) {
        uni.showToast({
          title: '至少保留一个地点',
          icon: 'none'
        });
        return;
      }
      const point = this.currentRoute[index];
      this.currentRoute.splice(index, 1);
      this.markers = this.markers.filter(marker => marker.id !== point.id);
      this.resetTransportTimes();
      this.polylines = [];
      if (this.activeRouteIndex >= index) {
        this.activeRouteIndex = Math.max(0, this.activeRouteIndex - 1);
      }
      uni.showToast({
        title: '地点已移除',
        icon: 'success'
      });
    },
    
    replanRoute() {
      if (this.currentRoute.length === 0) {
        uni.showToast({
          title: '请先添加地点',
          icon: 'none'
        });
        return;
      }
      uni.showModal({
        title: '重新规划路线',
        content: '这将清除当前路线并重新开始规划，确定继续吗？',
        confirmColor: '#b8d4ff',
        success: (res) => {
          if (res.confirm) {
            this.markers = this.markers.filter(marker => marker.id === 0);
            this.currentRoute = [];
            this.polylines = [];
            this.activeRouteIndex = 0;
            this.selectedRouteId = null;
            this.resetTransportTimes();
            uni.showToast({
              title: '已清除路线，请重新添加地点',
              icon: 'success'
            });
          }
        }
      });
    },
    
    clearRoute() {
      if (this.currentRoute.length === 0) {
        uni.showToast({
          title: '当前没有路线可清除',
          icon: 'none'
        });
        return;
      }
      uni.showModal({
        title: '提示',
        content: '确定清除当前路线吗？',
        confirmColor: '#b8d4ff',
        success: (res) => {
          if (res.confirm) {
            this.markers = this.markers.filter(marker => marker.id === 0);
            this.currentRoute = [];
            this.polylines = [];
            this.activeRouteIndex = 0;
            this.selectedRouteId = null;
            this.resetTransportTimes();
            this.refreshMap();
            uni.showToast({
              title: '路线已清除',
              icon: 'success'
            });
          }
        }
      });
    },
    
    goToWeather(point) {
      uni.navigateTo({
        url: `/pages/weather/weather?location=${encodeURIComponent(point.name)}`
      });
    },
    
    saveRoute() {
      if (this.currentRoute.length === 0) {
        uni.showToast({
          title: '请先添加地点再保存',
          icon: 'none'
        });
        return;
      }
      uni.showLoading({
        title: '保存中...'
      });
      setTimeout(() => {
        uni.hideLoading();
        const savedRoutes = uni.getStorageSync('user_routes') || [];
        const newRoute = {
          id: Date.now(),
          name: `我的路线 ${new Date().toLocaleDateString()}`,
          description: `包含${this.currentRoute.length}个地点的旅行路线`,
          places: this.currentRoute.map(point => point.name),
          duration: Math.ceil(this.currentRoute.length / 2),
          distance: Math.round(this.currentRoute.length * 50),
          tags: ['自定义', '最新'],
          createTime: new Date().toISOString(),
          coordinates: this.currentRoute.map(point => ({
            name: point.name,
            latitude: point.latitude,
            longitude: point.longitude
          }))
        };
        savedRoutes.unshift(newRoute);
        uni.setStorageSync('user_routes', savedRoutes);
        this.savedRoutes = savedRoutes;
        uni.$emit('routesUpdated');
        uni.showToast({
          title: '路线保存成功',
          icon: 'success'
        });
      }, 1500);
    },
    
    shareRoute() {
      if (this.currentRoute.length === 0) {
        uni.showToast({
          title: '请先规划路线再分享',
          icon: 'none'
        });
        return;
      }
      uni.showActionSheet({
        itemList: ['分享给好友', '生成路线图', '复制链接'],
        success: (res) => {
          uni.showToast({
            title: '分享功能开发中',
            icon: 'none'
          });
        }
      });
    },
    
    loadHotStrategies() {},
    
    viewMoreStrategies() {
      uni.navigateTo({
        url: '/pages/strategy/strategy'
      });
    },
    
    viewStrategy(strategy) {
      uni.navigateTo({
        url: `/pages/strategy/detail?id=${strategy.id}`
      });
    },
    
    viewMoreNearby() {
      uni.navigateTo({
        url: '/pages/nearby/nearby'
      });
    },
    
    viewNearbyPlace(place) {
      uni.showToast({
        title: `查看${place.name}`,
        icon: 'none'
      });
    },
    
    checkFirstVisit() {
      const hasVisited = uni.getStorageSync('has_visited_map');
      if (!hasVisited) {
        this.showAddPointTip = true;
        uni.setStorageSync('has_visited_map', true);
      }
    },
    
    hideAddPointTip() {
      this.showAddPointTip = false;
    },
    
    // ================== 心知天气 API ==================
    async getTemperatureForLocation(latitude, longitude) {
      const cacheKey = `${latitude.toFixed(2)},${longitude.toFixed(2)}`;
      if (this.weatherCache.has(cacheKey)) {
        return this.weatherCache.get(cacheKey);
      }
      try {
        const location = `${latitude}:${longitude}`;
        const url = `${this.seniverseBaseUrl}?key=${this.seniverseKey}&location=${location}&language=zh-Hans&unit=c`;
        console.log('请求心知天气 API:', url);
        const response = await new Promise((resolve, reject) => {
          uni.request({
            url: url,
            method: 'GET',
            timeout: 10000,
            success: (res) => {
              console.log('心知天气 API 响应:', res);
              if (res.statusCode === 200 && res.data && res.data.results && res.data.results.length > 0) {
                resolve(res.data);
              } else {
                reject(new Error(res.data?.message || '天气 API 请求失败'));
              }
            },
            fail: (error) => {
              reject(error);
            }
          });
        });
        const weatherData = response.results[0].now;
        const temperature = weatherData.temperature;
        const weatherText = weatherData.text;
        const weatherDisplay = `${temperature}°C ${weatherText}`;
        this.weatherCache.set(cacheKey, weatherDisplay);
        setTimeout(() => {
          this.weatherCache.delete(cacheKey);
        }, 60 * 60 * 1000);
        return weatherDisplay;
      } catch (error) {
        console.error('获取心知天气信息失败:', error);
        const defaultWeather = '25°C 晴';
        this.weatherCache.set(cacheKey, defaultWeather);
        return defaultWeather;
      }
    },

    // ================== 新增：起点终点选择相关方法 ==================
    onStartChange(e) {
      const index = e.detail.value;
      if (index === this.selectedEndIndex) {
        uni.showToast({
          title: '起点和终点不能相同',
          icon: 'none'
        });
        return;
      }
      this.selectedStartIndex = index;
    },

    onEndChange(e) {
      const index = e.detail.value;
      if (index === this.selectedStartIndex) {
        uni.showToast({
          title: '起点和终点不能相同',
          icon: 'none'
        });
        return;
      }
      this.selectedEndIndex = index;
    },

    applyStartEndOrder() {
      if (this.currentRoute.length < 2) {
        uni.showToast({
          title: '至少需要两个地点才能调整顺序',
          icon: 'none'
        });
        return;
      }

      if (this.selectedStartIndex === this.selectedEndIndex) {
        uni.showToast({
          title: '起点和终点不能相同',
          icon: 'none'
        });
        return;
      }

      // 获取起点和终点对象
      const startPoint = this.currentRoute[this.selectedStartIndex];
      const endPoint = this.currentRoute[this.selectedEndIndex];

      // 获取其他地点（保持原有顺序，排除起点和终点）
      const otherPoints = this.currentRoute.filter((_, index) => 
        index !== this.selectedStartIndex && index !== this.selectedEndIndex
      );

      // 重新构建路线顺序：[起点, ...其他地点, 终点]
      const newOrder = [startPoint, ...otherPoints, endPoint];

      // 更新当前路线
      this.currentRoute = newOrder;

      // 重置路线规划相关状态
      this.resetTransportTimes();
      this.polylines = [];
      this.activeRouteIndex = 0;

      // 更新起点/终点选择器的默认值（新顺序中起点索引0，终点索引最后一个）
      this.selectedStartIndex = 0;
      this.selectedEndIndex = this.currentRoute.length - 1;

      // 刷新地图显示
      this.focusOnRoute();
      
      uni.showToast({
        title: '路线顺序已更新',
        icon: 'success'
      });
    }
  }
}
</script>

<style scoped>
.map-page {
  height: 100vh;
  background-color: #f8f8f8;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ================== 优化后的搜索栏样式 ================== */
.search-section {
  background: #fff;
  padding: 20rpx 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
  flex-shrink: 0;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.03);
}

.search-bar-container {
  display: flex;
  align-items: center;
}

.search-bar {
  flex: 1;
  display: flex;
  align-items: center;
  background: #f5f7fa;
  border-radius: 60rpx;
  padding: 12rpx 20rpx;
  transition: all 0.3s ease;
  border: 1rpx solid #eef2f6;
}

.search-bar:active {
  background: #eef2f6;
  transform: scale(0.98);
}

.search-icon-wrapper {
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12rpx;
  background: rgba(184, 212, 255, 0.2);
  border-radius: 50%;
}

.search-icon {
  width: 28rpx;
  height: 28rpx;
}

.search-input {
  flex: 1;
  font-size: 28rpx;
  color: #333;
  line-height: 1.5;
}

.search-input::placeholder {
  color: #aaa;
  font-size: 26rpx;
}

.search-clear {
  width: 44rpx;
  height: 44rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.08);
  border-radius: 50%;
}

.search-clear .clear-icon {
  width: 24rpx;
  height: 24rpx;
}

.search-voice {
  width: 44rpx;
  height: 44rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 8rpx;
}

.voice-icon {
  width: 32rpx;
  height: 32rpx;
  opacity: 0.6;
}

/* ================== 优化后的搜索结果面板 ================== */
.search-results-panel {
  position: absolute;
  top: 120rpx;
  left: 30rpx;
  right: 30rpx;
  background: #fff;
  border-radius: 32rpx;
  box-shadow: 0 16rpx 48rpx rgba(0, 0, 0, 0.12);
  z-index: 1000;
  max-height: 600rpx;
  overflow: hidden;
  backdrop-filter: blur(20rpx);
  border: 1rpx solid rgba(255, 255, 255, 0.2);
}

.search-results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 28rpx 32rpx;
  border-bottom: 1rpx solid #f0f0f0;
  background: #fff;
}

.results-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #1a2a3a;
}

.results-close {
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  border-radius: 50%;
}

.results-close:active {
  background: #e8e8e8;
}

.search-results-list {
  max-height: 500rpx;
}

/* 搜索结果项样式 */
.search-result-item {
  display: flex;
  align-items: center;
  padding: 28rpx 32rpx;
  border-bottom: 1rpx solid #f8f8f8;
  transition: background 0.2s ease;
}

.search-result-item:active {
  background-color: #f8f9fc;
}

.result-icon {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 24rpx;
}

.result-icon-inner {
  width: 56rpx;
  height: 56rpx;
  background: linear-gradient(135deg, #e8f1ff 0%, #d4e5fc 100%);
  border-radius: 28rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.location-icon {
  width: 32rpx;
  height: 32rpx;
}

.result-content {
  flex: 1;
  overflow: hidden;
}

.result-title {
  font-size: 30rpx;
  color: #1a2a3a;
  display: block;
  margin-bottom: 8rpx;
  font-weight: 600;
  line-height: 1.3;
}

.result-address {
  font-size: 24rpx;
  color: #8a9aac;
  display: block;
  margin-bottom: 6rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.result-tags {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.result-region {
  font-size: 22rpx;
  color: #b8d4ff;
  background: rgba(184, 212, 255, 0.15);
  padding: 4rpx 12rpx;
  border-radius: 16rpx;
}

.result-distance {
  font-size: 26rpx;
  color: #b8d4ff;
  font-weight: 500;
  background: rgba(184, 212, 255, 0.12);
  padding: 8rpx 16rpx;
  border-radius: 24rpx;
}

/* ================== 全屏搜索页面样式（优化后） ================== */
.search-page {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #ffffff;
  z-index: 2000;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.search-page-header {
  background: #fff;
  padding: 20rpx 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
}

.search-page-bar {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.back-btn {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.back-btn:active {
  background: #e8ecf2;
  transform: scale(0.95);
}

.back-icon {
  width: 32rpx;
  height: 32rpx;
}

.search-input-container {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
  background: #f5f7fa;
  border-radius: 48rpx;
  padding: 0 20rpx;
  transition: all 0.3s ease;
  border: 1rpx solid #eef2f6;
}

.search-input-container:focus-within {
  border-color: #b8d4ff;
  background: #fff;
  box-shadow: 0 0 0 4rpx rgba(184, 212, 255, 0.2);
}

.search-input-icon {
  width: 32rpx;
  height: 32rpx;
  margin-right: 16rpx;
  opacity: 0.6;
}

.search-page-input {
  flex: 1;
  font-size: 30rpx;
  color: #1a2a3a;
  padding: 24rpx 0;
  background: transparent;
}

.search-page-input::placeholder {
  color: #b0bec5;
  font-size: 28rpx;
}

.search-page-clear {
  width: 44rpx;
  height: 44rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.08);
  border-radius: 50%;
  margin-left: 12rpx;
}

.search-page-clear .clear-icon {
  width: 22rpx;
  height: 22rpx;
}

.search-btn {
  background: #b8d4ff;
  padding: 16rpx 32rpx;
  border-radius: 48rpx;
  font-size: 28rpx;
  color: #fff;
  font-weight: 600;
  transition: all 0.2s ease;
  box-shadow: 0 4rpx 12rpx rgba(184, 212, 255, 0.3);
}

.search-btn:active {
  transform: scale(0.95);
  background: #a0c0f0;
  box-shadow: 0 2rpx 8rpx rgba(184, 212, 255, 0.4);
}

/* 搜索历史区域 */
.search-history {
  padding: 32rpx 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.history-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #1a2a3a;
}

.clear-history {
  width: 56rpx;
  height: 56rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  border-radius: 50%;
}

.clear-history:active {
  background: #e8e8e8;
}

.clear-history .clear-icon {
  width: 28rpx;
  height: 28rpx;
}

.history-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 12rpx;
  background: #f5f7fa;
  padding: 16rpx 28rpx;
  border-radius: 48rpx;
  transition: all 0.2s ease;
}

.history-item:active {
  background: #e8ecf2;
  transform: scale(0.96);
}

.history-icon {
  width: 28rpx;
  height: 28rpx;
  opacity: 0.6;
}

.history-text {
  font-size: 26rpx;
  color: #4a5a6a;
}

/* 热门搜索区域 */
.hot-search {
  padding: 32rpx 30rpx;
}

.hot-header {
  margin-bottom: 24rpx;
}

.hot-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #1a2a3a;
}

.hot-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
}

.hot-item {
  background: linear-gradient(135deg, #fff5f0 0%, #ffece3 100%);
  padding: 16rpx 32rpx;
  border-radius: 48rpx;
  transition: all 0.2s ease;
  border: 1rpx solid rgba(255, 107, 107, 0.2);
}

.hot-item:active {
  transform: scale(0.96);
  background: linear-gradient(135deg, #ffece3 0%, #ffe0d4 100%);
}

.hot-text {
  font-size: 26rpx;
  color: #ff6b6b;
  font-weight: 500;
}

/* 搜索页面结果列表 */
.search-page-results {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #fff;
}

.search-page-results-list {
  flex: 1;
}

.search-page-result-item {
  display: flex;
  align-items: center;
  padding: 28rpx 30rpx;
  border-bottom: 1rpx solid #f5f5f5;
  transition: background 0.2s ease;
}

.search-page-result-item:active {
  background: #f8f9fc;
}

/* 无结果状态 */
.no-results {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80rpx 40rpx;
}

.no-results-icon {
  width: 160rpx;
  height: 160rpx;
  margin-bottom: 32rpx;
  opacity: 0.5;
}

.no-results-text {
  font-size: 32rpx;
  color: #8a9aac;
  margin-bottom: 12rpx;
  font-weight: 500;
}

.no-results-desc {
  font-size: 26rpx;
  color: #b0bec5;
}

/* ================== 其余原有样式保持不变 ================== */
.function-buttons {
  background: #fff;
  padding: 25rpx 30rpx;
  border-bottom: 1rpx solid #eee;
  flex-shrink: 0;
}

.button-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 25rpx;
}

.button-row:last-child {
  margin-bottom: 0;
}

.function-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 20%;
}

.button-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 15rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.function-button:active .button-icon {
  transform: scale(0.95);
  box-shadow: 0 2rpx 6rpx rgba(0, 0, 0, 0.12);
}

.icon-image {
  width: 65rpx;
  height: 65rpx;
}

.button-text {
  font-size: 22rpx;
  color: #333;
  font-weight: 500;
}

.main-scroll {
  flex: 1;
  height: 100%;
  -webkit-overflow-scrolling: touch;
}

.map-container {
  position: relative;
  background: #f0f0f0;
  transition: transform 0.3s ease;
}

.map {
  width: 100%;
  height: 100%;
}

.map-controls {
  position: absolute;
  right: 30rpx;
  top: 30rpx;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 20rpx;
  box-shadow: 0 8rpx 30rpx rgba(0, 0, 0, 0.15);
  overflow: hidden;
  z-index: 100;
}

.control-btn {
  width: 90rpx;
  height: 90rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1rpx solid #f5f5f5;
  transition: all 0.3s ease;
  position: relative;
}

.control-btn:active {
  background-color: #f8f8f8;
  transform: scale(0.95);
}

.control-btn:last-child {
  border-bottom: none;
}

.control-icon {
  width: 36rpx;
  height: 36rpx;
}

.control-btn.view-all {
  background: #b8d4ff;
}

.control-btn.view-all:active {
  background: #a0c0ff;
}

.location-status {
  position: absolute;
  top: 30rpx;
  left: 30rpx;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  padding: 12rpx 20rpx;
  border-radius: 20rpx;
  font-size: 24rpx;
  z-index: 100;
}

.status-text {
  color: #fff;
}

.content-panel {
  background: #fff;
  border-top-left-radius: 30rpx;
  border-top-right-radius: 30rpx;
  margin-top: -25rpx;
  position: relative;
  z-index: 10;
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.06);
  min-height: 600rpx;
}

.route-section, .strategy-section, .nearby-section {
  padding: 35rpx 30rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28rpx;
}

.section-title {
  font-size: 34rpx;
  font-weight: 700;
  color: #333;
  position: relative;
  padding-left: 20rpx;
}

.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 6rpx;
  height: 28rpx;
  background: #b8d4ff;
  border-radius: 3rpx;
}

.route-actions {
  display: flex;
  gap: 20rpx;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 10rpx;
  font-size: 24rpx;
  color: #b8d4ff;
  padding: 12rpx 20rpx;
  background: #e8f1ff;
  border-radius: 25rpx;
  transition: all 0.3s ease;
}

.action-btn.clear {
  background: #ffeaea;
  color: #ff6b6b;
}

.action-btn.my-routes {
  background: #f0f8ff;
  color: #4a90e2;
}

.action-btn.disabled {
  opacity: 0.5;
  pointer-events: none;
}

.action-btn:active {
  transform: scale(0.95);
}

.action-icon {
  width: 24rpx;
  height: 24rpx;
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

.route-selector {
  background: #f8fbff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  border: 1rpx solid #e1edff;
}

.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.selector-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #2c5282;
}

.selector-actions {
  display: flex;
  gap: 12rpx;
}

.selector-btn {
  display: flex;
  align-items: center;
  gap: 6rpx;
  font-size: 22rpx;
  color: #5a7ca8;
  padding: 8rpx 16rpx;
  background: rgba(184, 212, 255, 0.3);
  border-radius: 12rpx;
}

.selector-icon {
  width: 20rpx;
  height: 20rpx;
}

.route-selector-list {
  white-space: nowrap;
}

.route-selector-item {
  display: inline-flex;
  align-items: center;
  background: #ffffff;
  border-radius: 14rpx;
  padding: 20rpx;
  margin-right: 16rpx;
  min-width: 280rpx;
  border: 2rpx solid transparent;
  transition: all 0.3s ease;
  box-shadow: 0 2rpx 8rpx rgba(184, 212, 255, 0.2);
}

.route-selector-item.active {
  border-color: #b8d4ff;
  background: #f0f7ff;
  box-shadow: 0 4rpx 12rpx rgba(184, 212, 255, 0.4);
}

.route-selector-item:active {
  transform: scale(0.98);
}

.route-selector-content {
  flex: 1;
  margin-right: 16rpx;
}

.route-selector-name {
  font-size: 26rpx;
  color: #2c5282;
  font-weight: 600;
  display: block;
  margin-bottom: 8rpx;
}

.route-selector-info {
  font-size: 22rpx;
  color: #5a7ca8;
  display: block;
  margin-bottom: 8rpx;
}

.route-selector-tags {
  display: flex;
  gap: 8rpx;
}

.route-tag {
  font-size: 18rpx;
  color: #b8d4ff;
  background: rgba(184, 212, 255, 0.2);
  padding: 4rpx 10rpx;
  border-radius: 10rpx;
  border: 1rpx solid rgba(184, 212, 255, 0.3);
}

.route-selector-actions {
  display: flex;
  gap: 8rpx;
}

.route-action-btn {
  width: 44rpx;
  height: 44rpx;
  border-radius: 10rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.route-action-btn.view {
  background: rgba(184, 212, 255, 0.3);
}

.route-action-btn.delete {
  background: rgba(255, 107, 107, 0.1);
}

.route-action-btn:active {
  transform: scale(0.9);
}

.current-route-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.current-route-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
}

.current-route-count {
  font-size: 24rpx;
  color: #999;
  background: #f5f5f5;
  padding: 6rpx 12rpx;
  border-radius: 12rpx;
}

/* 新增起点终点选择器样式 */
.start-end-selector {
  background: #f0f7ff;
  border-radius: 20rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  border: 1rpx solid #e1edff;
}

.selector-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
}

.selector-row:last-of-type {
  margin-bottom: 0;
}

.selector-label {
  font-size: 28rpx;
  font-weight: 500;
  color: #2c5282;
  width: 80rpx;
}

.picker-content {
  flex: 1;
  background: #ffffff;
  padding: 16rpx 24rpx;
  border-radius: 40rpx;
  font-size: 28rpx;
  color: #1a2a3a;
  border: 1rpx solid #d4e5fc;
  text-align: center;
}

.apply-order-btn {
  margin-top: 20rpx;
  background: #b8d4ff;
  border-radius: 48rpx;
  padding: 16rpx 0;
  text-align: center;
  transition: all 0.2s ease;
}

.apply-order-btn:active {
  transform: scale(0.98);
  background: #a0c0f0;
}

.apply-order-btn text {
  color: #fff;
  font-size: 28rpx;
  font-weight: 500;
}

.route-content {
  background: #f8f8f8;
  border-radius: 20rpx;
  padding: 28rpx;
}

.route-list {
  white-space: nowrap;
  margin-bottom: 28rpx;
}

.route-item {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  padding: 24rpx;
  background: #fff;
  border-radius: 16rpx;
  margin-right: 20rpx;
  min-width: 160rpx;
  transition: all 0.3s ease;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.06);
  position: relative;
}

.route-item:active {
  background-color: #f5f5f5;
  transform: scale(0.98);
}

.route-item.active {
  background: #e8f1ff;
  border: 2rpx solid #b8d4ff;
  box-shadow: 0 6rpx 20rpx rgba(184, 212, 255, 0.3);
}

.route-order {
  width: 48rpx;
  height: 48rpx;
  background: #b8d4ff;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  font-weight: 600;
  margin-bottom: 16rpx;
  box-shadow: 0 4rpx 8rpx rgba(184, 212, 255, 0.4);
}

.route-name {
  font-size: 26rpx;
  color: #333;
  margin-bottom: 12rpx;
  text-align: center;
  font-weight: 500;
}

.route-weather {
  display: flex;
  align-items: center;
  gap: 6rpx;
  font-size: 20rpx;
  color: #b8d4ff;
  margin-bottom: 12rpx;
}

.weather-icon {
  width: 40rpx;
  height: 40rpx;
}

.route-suggestion {
  border-top: 1rpx solid #eee;
  padding-top: 24rpx;
  margin-bottom: 24rpx;
}

.suggestion-title {
  font-size: 26rpx;
  color: #333;
  margin-bottom: 20rpx;
  display: block;
  font-weight: 600;
}

.transport-options {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.transport-option {
  display: flex;
  align-items: center;
  gap: 10rpx;
  padding: 16rpx 24rpx;
  background: #f5f5f5;
  border-radius: 25rpx;
  font-size: 24rpx;
  color: #666;
  transition: all 0.3s ease;
  flex: 1;
  min-width: 0;
  justify-content: center;
}

.transport-option:active {
  background-color: #e8f1ff;
  transform: scale(0.98);
}

.transport-option.active {
  background: #b8d4ff;
  color: #fff;
  box-shadow: 0 4rpx 12rpx rgba(184, 212, 255, 0.4);
}

.transport-icon {
  width: 50rpx;
  height: 50rpx;
}

.transport-time {
  font-size: 20rpx;
  opacity: 0.8;
}

.route-details {
  background: #ffffff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-top: 24rpx;
  border: 1rpx solid #e8f1ff;
  box-shadow: 0 2rpx 10rpx rgba(184, 212, 255, 0.2);
}

.route-details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
  padding-bottom: 16rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.details-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #2c5282;
}

.details-summary {
  display: flex;
  gap: 20rpx;
}

.summary-item {
  font-size: 22rpx;
  color: #5a7ca8;
  background: rgba(184, 212, 255, 0.2);
  padding: 6rpx 12rpx;
  border-radius: 10rpx;
}

.route-steps {
  max-height: 300rpx;
}

.route-step {
  display: flex;
  align-items: flex-start;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #f8f8f8;
}

.route-step:last-child {
  border-bottom: none;
}

.step-number {
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
  margin-right: 16rpx;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-instruction {
  font-size: 26rpx;
  color: #333;
  display: block;
  margin-bottom: 6rpx;
  line-height: 1.4;
}

.step-distance {
  font-size: 22rpx;
  color: #b8d4ff;
  background: rgba(184, 212, 255, 0.1);
  padding: 4rpx 10rpx;
  border-radius: 8rpx;
}

.route-operations {
  display: flex;
  gap: 20rpx;
  margin-top: 20rpx;
}

.operation-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10rpx;
  flex: 1;
  padding: 20rpx;
  background: #f5f5f5;
  border-radius: 16rpx;
  font-size: 26rpx;
  color: #666;
  transition: all 0.3s ease;
}

.operation-btn.save {
  background: #e8f1ff;
  color: #b8d4ff;
}

.operation-btn.share {
  background: #f0f0f0;
  color: #666;
}

.operation-btn.disabled {
  opacity: 0.5;
  pointer-events: none;
}

.operation-btn:active {
  transform: scale(0.98);
}

.operation-icon {
  width: 28rpx;
  height: 28rpx;
}

.empty-route {
  text-align: center;
  padding: 80rpx 0;
}

.empty-icon {
  width: 120rpx;
  height: 120rpx;
  margin-bottom: 24rpx;
  opacity: 0.6;
}

.empty-text {
  font-size: 26rpx;
  color: #999;
  display: block;
  margin-bottom: 12rpx;
}

.empty-desc {
  font-size: 24rpx;
  color: #ccc;
  display: block;
  margin-bottom: 24rpx;
}

.empty-action {
  display: inline-block;
  background: #e8f1ff;
  padding: 16rpx 32rpx;
  border-radius: 25rpx;
  border: 1rpx solid #b8d4ff;
}

.empty-action-text {
  font-size: 24rpx;
  color: #b8d4ff;
  font-weight: 500;
}

.strategy-list {
  white-space: nowrap;
}

.strategy-item {
  display: inline-flex;
  flex-direction: column;
  width: 300rpx;
  background: #f8f8f8;
  border-radius: 20rpx;
  margin-right: 24rpx;
  overflow: hidden;
  transition: all 0.3s ease;
  position: relative;
  box-shadow: 0 4rpx 15rpx rgba(0, 0, 0, 0.08);
}

.strategy-item:active {
  background-color: #f0f0f0;
  transform: scale(0.98);
}

.strategy-badge {
  position: absolute;
  top: 16rpx;
  left: 16rpx;
  color: #fff;
  font-size: 20rpx;
  padding: 6rpx 12rpx;
  border-radius: 20rpx;
  z-index: 2;
}

.strategy-badge.hot {
  background: #ff6b6b;
}

.strategy-badge.featured {
  background: #b8d4ff;
}

.strategy-badge.new {
  background: #6bcf7f;
}

.strategy-image {
  width: 100%;
  height: 180rpx;
}

.strategy-info {
  padding: 24rpx;
}

.strategy-title {
  font-size: 28rpx;
  color: #333;
  display: block;
  margin-bottom: 20rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
}

.strategy-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 22rpx;
  color: #999;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.author-avatar {
  width: 36rpx;
  height: 36rpx;
  border-radius: 50%;
}

.likes-count {
  display: flex;
  align-items: center;
  gap: 6rpx;
}

.like-icon {
  width: 24rpx;
  height: 24rpx;
}

.nearby-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20rpx;
}

.nearby-item {
  background: #f8f8f8;
  border-radius: 16rpx;
  overflow: hidden;
  transition: all 0.3s ease;
}

.nearby-item:active {
  background: #f0f0f0;
  transform: scale(0.98);
}

.nearby-image {
  width: 100%;
  height: 160rpx;
}

.nearby-info {
  padding: 20rpx;
}

.nearby-name {
  font-size: 26rpx;
  color: #333;
  display: block;
  margin-bottom: 8rpx;
  font-weight: 500;
}

.nearby-type {
  font-size: 22rpx;
  color: #999;
  display: block;
  margin-bottom: 12rpx;
}

.nearby-distance {
  display: flex;
  align-items: center;
  gap: 6rpx;
  font-size: 22rpx;
  color: #b8d4ff;
}

.distance-icon {
  width: 20rpx;
  height: 20rpx;
}

.safe-area {
  height: env(safe-area-inset-bottom);
  background: #fff;
}

.add-point-tip {
  position: absolute;
  bottom: 30rpx;
  left: 30rpx;
  right: 30rpx;
  background: rgba(0, 0, 0, 0.8);
  color: #fff;
  padding: 20rpx 24rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 100;
}

.tip-close {
  width: 32rpx;
  height: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-icon {
  width: 20rpx;
  height: 20rpx;
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