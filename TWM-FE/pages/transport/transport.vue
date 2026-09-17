<template>
  <view class="transport-page">
    <!-- 顶部导航栏 -->
    <view class="nav-bar">
      <view class="nav-item" :class="{ active: currentTab === 'airplane' }" @tap="switchTab('airplane')">
        <text class="nav-text">机票</text>
      </view>
      <view class="nav-item" :class="{ active: currentTab === 'train' }" @tap="switchTab('train')">
        <text class="nav-text">火车高铁</text>
      </view>
      <view class="nav-item" :class="{ active: currentTab === 'bus' }" @tap="switchTab('bus')">
        <text class="nav-text">大巴</text>
      </view>
      <view class="nav-item" :class="{ active: currentTab === 'car' }" @tap="switchTab('car')">
        <text class="nav-text">租车/包车</text>
      </view>
      <view class="nav-item" :class="{ active: currentTab === 'public' }" @tap="navigateToBusPage">
        <text class="nav-text">公交/地铁</text>
      </view>
    </view>

    <view class="content-section">
      <!-- 机票内容 -->
      <view class="tab-content" v-if="currentTab === 'airplane'">
        <scroll-view class="content-scroll" scroll-y :refresher-enabled="true"
          :refresher-triggered="airplaneRefreshing" @refresherrefresh="onRefreshAirplane">

          <view class="city-selector-bar">
            <view class="city-select-item">
              <text class="city-label">出发城市</text>
              <view class="input-wrapper">
                <input type="text" v-model="airDepartureInput" placeholder="请输入城市名称"
                  @focus="onCityInputFocus('departure')" @input="onCityInput('departure', airDepartureInput)"
                  @blur="hideSuggestionsDelayed('departure')" class="city-input" />
                <view class="suggestions-list" v-if="showDepartureSuggestions && departureSuggestions.length">
                  <view class="suggestion-item" v-for="city in departureSuggestions" :key="city.id"
                    @mousedown.stop @click="selectDepartureCity(city)">
                    {{ city.name }}
                  </view>
                </view>
              </view>
            </view>
            <view class="city-swap" @tap="swapAirportCities">
              <image class="swap-icon" src="/static/icons/transport/swap.png" mode="aspectFit"></image>
            </view>
            <view class="city-select-item">
              <text class="city-label">到达城市</text>
              <view class="input-wrapper">
                <input type="text" v-model="airArrivalInput" placeholder="请输入城市名称"
                  @focus="onCityInputFocus('arrival')" @input="onCityInput('arrival', airArrivalInput)"
                  @blur="hideSuggestionsDelayed('arrival')" class="city-input" />
                <view class="suggestions-list" v-if="showArrivalSuggestions && arrivalSuggestions.length">
                  <view class="suggestion-item" v-for="city in arrivalSuggestions" :key="city.id"
                    @mousedown.stop @click="selectArrivalCity(city)">
                    {{ city.name }}
                  </view>
                </view>
              </view>
            </view>
          </view>

          <view class="date-selector-bar">
            <text class="date-label">出发日期</text>
            <picker mode="date" :value="flightDate" @change="onFlightDateChange" :start="minDate">
              <view class="date-picker-display">{{ formattedFlightDate }}</view>
            </picker>
          </view>

          <view class="search-btn" @tap="searchAirplane">
            <text class="search-btn-text">搜索航班</text>
          </view>

          <view class="flight-list" v-if="!airplaneLoading && airplaneList.length">
            <view class="flight-card" v-for="flight in airplaneList" :key="flight.id" @tap="viewFlightDetail(flight)">
              <view class="flight-header">
                <view class="flight-route">
                  <text class="city">{{ flight.departure.city }}</text>
                  <image class="route-arrow" src="/static/icons/transport/arrow-right.png"></image>
                  <text class="city">{{ flight.arrival.city }}</text>
                </view>
                <view class="flight-date-wrapper">
                  <text class="flight-date-text">{{ flight.departureDate }}</text>
                </view>
                <view class="flight-price">
                  <text class="price">￥{{ flight.price }}</text>
                  <text class="price-desc">起</text>
                </view>
              </view>
              <view class="flight-detail">
                <view class="time-section">
                  <text class="time">{{ flight.departure.time }}</text>
                  <text class="airport">{{ flight.departure.airport }}</text>
                </view>
                <view class="duration-section">
                  <text class="duration">{{ flight.duration }}</text>
                  <view class="flight-line">
                    <view class="line-dot start"></view>
                    <view class="line"></view>
                    <view class="line-dot end"></view>
                  </view>
                  <text class="flight-type">{{ flight.type }}</text>
                </view>
                <view class="time-section">
                  <text class="time">{{ flight.arrival.time }}</text>
                  <text class="airport">{{ flight.arrival.airport }}</text>
                </view>
              </view>
              <view class="flight-footer">
                <text class="airline">{{ flight.airline }}</text>
                <text class="flight-number">{{ flight.flightNumber }}</text>
                <view class="discount-tag" v-if="flight.discount">{{ flight.discount }}</view>
              </view>
            </view>
          </view>
          <view v-if="airplaneLoading" class="loading-container">
            <text class="loading-text">正在搜索航班...</text>
          </view>
          <view v-if="!airplaneLoading && airplaneList.length === 0" class="empty-container">
            <text class="empty-text">{{ airplaneEmptyMsg || '暂无航班，请选择其他城市' }}</text>
          </view>
        </scroll-view>
      </view>

      <!-- 火车高铁内容 -->
      <view class="tab-content" v-if="currentTab === 'train'">
        <scroll-view class="content-scroll" scroll-y :refresher-enabled="true"
          :refresher-triggered="trainRefreshing" @refresherrefresh="onRefreshTrain">

          <view class="city-selector-bar">
            <view class="city-select-item">
              <text class="city-label">出发站/城市</text>
              <view class="input-wrapper">
                <input type="text" v-model="trainDepartureInput" placeholder="请输入城市或车站名（如：广州、广州南）"
                  @focus="showTrainDepartureSuggestions = true" @input="onTrainStationInput('departure')"
                  @blur="hideSuggestionsDelayed('trainDeparture')" class="city-input" />
                <view class="suggestions-list" v-if="showTrainDepartureSuggestions && trainDepartureSuggestions.length">
                  <view class="suggestion-item" v-for="station in trainDepartureSuggestions" :key="station.id"
                    @mousedown.stop @click="selectTrainDepartureStation(station)">
                    {{ station.title }}
                  </view>
                </view>
              </view>
            </view>
            <view class="city-swap" @tap="swapTrainStations">
              <image class="swap-icon" src="/static/icons/transport/swap.png" mode="aspectFit"></image>
            </view>
            <view class="city-select-item">
              <text class="city-label">到达站/城市</text>
              <view class="input-wrapper">
                <input type="text" v-model="trainArrivalInput" placeholder="请输入城市或车站名（如：珠海、珠海长隆）"
                  @focus="showTrainArrivalSuggestions = true" @input="onTrainStationInput('arrival')"
                  @blur="hideSuggestionsDelayed('trainArrival')" class="city-input" />
                <view class="suggestions-list" v-if="showTrainArrivalSuggestions && trainArrivalSuggestions.length">
                  <view class="suggestion-item" v-for="station in trainArrivalSuggestions" :key="station.id"
                    @mousedown.stop @click="selectTrainArrivalStation(station)">
                    {{ station.title }}
                  </view>
                </view>
              </view>
            </view>
          </view>

          <view class="date-selector-bar">
            <text class="date-label">出发日期</text>
            <picker mode="date" :value="trainDate" @change="onTrainDateChange" :start="minDate">
              <view class="date-picker-display">{{ formattedTrainDate }}</view>
            </picker>
          </view>

          <view class="search-btn" @tap="searchTrain">
            <text class="search-btn-text">搜索车次</text>
          </view>

          <view class="train-list" v-if="!trainLoading && trainList.length">
            <view class="train-card" v-for="item in trainList" :key="item.id" @tap="viewTrainDetail(item)">
              <view class="train-header">
                <view class="train-info">
                  <text class="train-number">{{ item.trainNumber }}</text>
                  <text class="train-type">{{ item.type }}</text>
                </view>
                <view class="train-price">
                  <text class="price">￥{{ item.price }}</text>
                  <text class="price-desc">起</text>
                </view>
              </view>
              <view class="train-route">
                <view class="station-section">
                  <text class="time">{{ item.departure.time }}</text>
                  <text class="station">{{ item.departure.station }}</text>
                </view>
                <view class="duration-section">
                  <text class="duration">{{ item.duration }}</text>
                  <view class="route-line">
                    <view class="line-dot start"></view>
                    <view class="line"></view>
                    <view class="line-dot end"></view>
                  </view>
                </view>
                <view class="station-section">
                  <text class="time">{{ item.arrival.time }}</text>
                  <text class="station">{{ item.arrival.station }}</text>
                </view>
              </view>
              <view class="train-seats">
                <text class="seat-item" v-for="seat in item.availableSeats" :key="seat.type">{{ seat.type }}: {{ seat.count }}张</text>
              </view>
              <view class="train-date-info" v-if="item.departureDate">
                <text class="date-text">{{ item.departureDate }}</text>
              </view>
            </view>
          </view>
          <view v-if="trainLoading && trainList.length === 0" class="loading-container">
            <text class="loading-text">正在搜索车次...</text>
          </view>
          <view v-if="!trainLoading && trainList.length === 0" class="empty-container">
            <text class="empty-text">{{ trainEmptyMsg || '暂无车次，请尝试其他日期或车站' }}</text>
          </view>
        </scroll-view>
      </view>

      <!-- 大巴内容 -->
      <view class="tab-content" v-if="currentTab === 'bus'">
        <scroll-view class="content-scroll" scroll-y :refresher-enabled="true"
          :refresher-triggered="busRefreshing" @refresherrefresh="onRefreshBus">

          <view class="city-selector-bar">
            <view class="city-select-item">
              <text class="city-label">出发城市</text>
              <view class="input-wrapper">
                <input type="text" v-model="busDepartureInput" placeholder="请输入城市"
                  @focus="showBusDepartureSuggestions = true" @input="onCityInput('busDeparture', busDepartureInput)"
                  @blur="hideSuggestionsDelayed('busDeparture')" class="city-input" />
                <view class="suggestions-list" v-if="showBusDepartureSuggestions && busDepartureSuggestions.length">
                  <view class="suggestion-item" v-for="city in busDepartureSuggestions" :key="city.id"
                    @mousedown.stop @click="selectBusDepartureCity(city)">
                    {{ city.name }}
                  </view>
                </view>
              </view>
            </view>
            <view class="city-swap" @tap="swapBusCities">
              <image class="swap-icon" src="/static/icons/transport/swap.png" mode="aspectFit"></image>
            </view>
            <view class="city-select-item">
              <text class="city-label">到达城市</text>
              <view class="input-wrapper">
                <input type="text" v-model="busArrivalInput" placeholder="请输入城市"
                  @focus="showBusArrivalSuggestions = true" @input="onCityInput('busArrival', busArrivalInput)"
                  @blur="hideSuggestionsDelayed('busArrival')" class="city-input" />
                <view class="suggestions-list" v-if="showBusArrivalSuggestions && busArrivalSuggestions.length">
                  <view class="suggestion-item" v-for="city in busArrivalSuggestions" :key="city.id"
                    @mousedown.stop @click="selectBusArrivalCity(city)">
                    {{ city.name }}
                  </view>
                </view>
              </view>
            </view>
          </view>

          <view class="date-selector-bar">
            <text class="date-label">出发日期</text>
            <picker mode="date" :value="busDate" @change="onBusDateChange" :start="minDate">
              <view class="date-picker-display">{{ formattedBusDate }}</view>
            </picker>
          </view>

          <view class="search-btn" @tap="searchBus">
            <text class="search-btn-text">搜索大巴</text>
          </view>

          <view class="bus-list" v-if="!busLoading && busList.length">
            <view class="bus-card" v-for="item in busList" :key="item.id" @tap="viewBusDetail(item)">
              <view class="bus-header">
                <view class="bus-route">
                  <text class="city">{{ item.departure.city }}</text>
                  <image class="route-arrow" src="/static/icons/transport/arrow-right.png"></image>
                  <text class="city">{{ item.arrival.city }}</text>
                </view>
                <view class="bus-price">
                  <text class="price">￥{{ item.price }}</text>
                </view>
              </view>
              <view class="bus-detail">
                <view class="time-section">
                  <text class="time">{{ item.departure.time }}</text>
                  <text class="station">{{ item.departure.station }}</text>
                </view>
                <view class="duration-section">
                  <text class="duration">{{ item.duration }}</text>
                </view>
                <view class="time-section">
                  <text class="time">{{ item.arrival.time }}</text>
                  <text class="station">{{ item.arrival.station }}</text>
                </view>
              </view>
              <view class="bus-footer">
                <text class="bus-type">{{ item.type }}</text>
                <text class="seats-available">剩余{{ item.availableSeats }}座</text>
              </view>
              <view class="bus-date-info" v-if="item.departureDate">
                <text class="date-text">{{ item.departureDate }}</text>
              </view>
            </view>
          </view>
          <view v-if="busLoading && busList.length === 0" class="loading-container">
            <text class="loading-text">正在搜索大巴...</text>
          </view>
          <view v-if="!busLoading && busList.length === 0" class="empty-container">
            <text class="empty-text">{{ busEmptyMsg || '暂无大巴班次' }}</text>
          </view>
        </scroll-view>
      </view>

      <!-- 租车内容（增加了日期选择） -->
      <view class="tab-content" v-if="currentTab === 'car'">
        <scroll-view class="content-scroll" scroll-y :refresher-enabled="true"
          :refresher-triggered="carRefreshing" @refresherrefresh="onRefreshCar">

          <view class="city-selector-bar single">
            <view class="city-select-item full">
              <text class="city-label">取车城市</text>
              <view class="input-wrapper">
                <input type="text" v-model="carPickupInput" placeholder="请输入城市"
                  @focus="showCarSuggestions = true" @input="onCityInput('car', carPickupInput)"
                  @blur="hideSuggestionsDelayed('car')" class="city-input" />
                <view class="suggestions-list" v-if="showCarSuggestions && carSuggestions.length">
                  <view class="suggestion-item" v-for="city in carSuggestions" :key="city.id"
                    @mousedown.stop @click="selectCarCity(city)">
                    {{ city.name }}
                  </view>
                </view>
              </view>
            </view>
          </view>

          <!-- 日期选择区域 - 新增 -->
          <view class="date-selector-bar dual">
            <view class="date-item">
              <text class="date-label">取车日期</text>
              <picker mode="date" :value="carPickupDate" @change="onCarPickupDateChange" :start="carMinDate">
                <view class="date-picker-display">{{ formattedCarPickupDate }}</view>
              </picker>
            </view>
            <view class="date-item">
              <text class="date-label">还车日期</text>
              <picker mode="date" :value="carReturnDate" @change="onCarReturnDateChange" :start="carPickupDate">
                <view class="date-picker-display">{{ formattedCarReturnDate }}</view>
              </picker>
            </view>
          </view>

          <view class="search-btn" @tap="searchCar">
            <text class="search-btn-text">搜索租车</text>
          </view>

          <view class="car-rental-list" v-if="!carLoading && carRentalList.length">
            <view class="car-rental-card" v-for="company in carRentalList" :key="company.id" @tap="viewCarRentalDetail(company)">
              <view class="company-header">
                <view class="company-info">
                  <text class="company-name">{{ company.name }}</text>
                  <text class="company-rating">★ {{ company.rating }}</text>
                </view>
                <view class="starting-price">
                  <text class="price">￥{{ company.totalStartingPrice }}</text>
                  <text class="price-desc">总价起</text>
                  <text class="daily-price">(日均￥{{ company.dailyStartingPrice }})</text>
                </view>
              </view>
              <view class="car-models">
                <scroll-view class="models-scroll" scroll-x>
                  <view class="car-model" v-for="model in company.popularModels" :key="model.name">
                    <text class="model-name">{{ model.name }}</text>
                    <text class="model-daily-price">￥{{ model.dailyPrice }}/天</text>
                    <text class="model-total-price">总价 ￥{{ model.totalPrice }}</text>
                  </view>
                </scroll-view>
              </view>
              <view class="company-features">
                <text class="feature-tag" v-for="feature in company.features" :key="feature">{{ feature }}</text>
              </view>
              <view class="rental-days">租期 {{ company.rentalDays }} 天</view>
            </view>
          </view>
          <view v-if="carLoading && carRentalList.length === 0" class="loading-container">
            <text class="loading-text">正在搜索租车公司...</text>
          </view>
          <view v-if="!carLoading && carRentalList.length === 0" class="empty-container">
            <text class="empty-text">{{ carEmptyMsg || '暂无租车公司' }}</text>
          </view>
        </scroll-view>
      </view>

      <!-- 公交/地铁入口 -->
      <view class="tab-content" v-if="currentTab === 'public'">
        <scroll-view class="content-scroll" scroll-y>
          <view class="public-transport-entry">
            <view class="entry-header">
              <text class="entry-title">公交地铁服务</text>
              <text class="entry-desc">提供实时公交、地铁线路、路线规划等全方位服务</text>
            </view>
            <view class="entry-cards">
              <view class="entry-card bus" @tap="navigateToBusPage('bus')">
                <view class="card-icon"><image src="/static/icons/transport/bus.png" mode="aspectFit"></image></view>
                <view class="card-content"><text class="card-title">实时公交</text><text class="card-desc">查看公交实时位置、到站时间</text></view>
                <view class="card-arrow"><image src="/static/icons/general/arrow-right.png" mode="aspectFit"></image></view>
              </view>
              <view class="entry-card subway" @tap="navigateToBusPage('subway')">
                <view class="card-icon"><image src="/static/icons/transport/subway.png" mode="aspectFit"></image></view>
                <view class="card-content"><text class="card-title">地铁线路</text><text class="card-desc">查看地铁线路图、站点信息</text></view>
                <view class="card-arrow"><image src="/static/icons/general/arrow-right.png" mode="aspectFit"></image></view>
              </view>
              <view class="entry-card route" @tap="navigateToBusPage('route')">
                <view class="card-icon"><image src="/static/icons/transport/route.png" mode="aspectFit"></image></view>
                <view class="card-content"><text class="card-title">路线规划</text><text class="card-desc">智能规划最佳出行路线</text></view>
                <view class="card-arrow"><image src="/static/icons/general/arrow-right.png" mode="aspectFit"></image></view>
              </view>
            </view>
            <view class="quick-action">
              <text class="action-title">快捷操作</text>
              <view class="action-buttons">
                <view class="action-btn" @tap="navigateToBusPage('bus')">
                  <image class="action-icon" src="/static/icons/transport/bus.png"></image>
                  <text>公交查询</text>
                </view>
                <view class="action-btn" @tap="navigateToBusPage('subway')">
                  <image class="action-icon" src="/static/icons/transport/subway.png"></image>
                  <text>地铁查询</text>
                </view>
                <view class="action-btn" @tap="navigateToBusPage('route')">
                  <image class="action-icon" src="/static/icons/transport/route-plan.png"></image>
                  <text>路线规划</text>
                </view>
              </view>
            </view>
          </view>
        </scroll-view>
      </view>
    </view>

    <!-- 定位权限弹窗 -->
    <view class="permission-modal" v-if="showPermissionModal">
      <view class="permission-content">
        <view class="permission-header"><text class="permission-title">位置权限申请</text></view>
        <view class="permission-body"><text class="permission-text">为了提供精准的出行服务，需要获取您的位置信息</text></view>
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
const QQ_MAP_KEY = '4DYBZ-7QXEC-CWM2S-AXAZR-YLVQF-C6BPY';
const QQ_MAP_API = 'https://apis.map.qq.com';

// 航空公司列表
const airlines = [
  { name: '中国国航', code: 'CA' }, { name: '东方航空', code: 'MU' },
  { name: '南方航空', code: 'CZ' }, { name: '海南航空', code: 'HU' },
  { name: '深圳航空', code: 'ZH' }, { name: '厦门航空', code: 'MF' },
  { name: '四川航空', code: '3U' }, { name: '山东航空', code: 'SC' }
];

// 租车公司列表
const carRentalCompanies = [
  { name: '神州租车', rating: 4.8, features: ['全国连锁', '免费送车', '24小时客服'] },
  { name: '一嗨租车', rating: 4.7, features: ['异地还车', '新车型多', '保险全包'] },
  { name: '悟空租车', rating: 4.5, features: ['经济实惠', '押金低', '灵活租期'] },
  { name: '滴滴租车', rating: 4.6, features: ['快速取还', '送车上门', '信用免押'] }
];

// 车型列表
const carModels = [
  { name: '大众朗逸', type: '紧凑型', basePrice: 120 },
  { name: '日产轩逸', type: '紧凑型', basePrice: 130 },
  { name: '丰田卡罗拉', type: '紧凑型', basePrice: 140 },
  { name: '本田雅阁', type: '中型', basePrice: 220 },
  { name: '别克GL8', type: 'MPV', basePrice: 350 },
  { name: '特斯拉Model 3', type: '新能源', basePrice: 380 },
  { name: '宝马3系', type: '豪华型', basePrice: 480 },
  { name: '奥迪A6L', type: '豪华型', basePrice: 600 }
];

// ========== 通用工具函数 ==========
function haversineDistance(lat1, lng1, lat2, lng2) {
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLng = (lng2 - lng1) * Math.PI / 180;
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLng / 2) * Math.sin(dLng / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

function formatDuration(minutes) {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours}小时${mins}分`;
}

function normalizeCityName(name) {
  if (!name) return '';
  const suffixes = ['市', '区', '县', '自治州', '盟', '地区', '林区', '特别行政区'];
  let normalized = name;
  for (const suffix of suffixes) {
    if (normalized.endsWith(suffix)) {
      normalized = normalized.slice(0, -suffix.length);
      break;
    }
  }
  return normalized;
}

function formatDateMD(dateStr) {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  const month = date.getMonth() + 1;
  const day = date.getDate();
  return `${month}月${day}日`;
}

// 计算两个日期之间的天数差
function getDaysBetween(date1, date2) {
  const d1 = new Date(date1);
  const d2 = new Date(date2);
  d1.setHours(0, 0, 0, 0);
  d2.setHours(0, 0, 0, 0);
  const diffTime = Math.abs(d2 - d1);
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

// 获取租车价格因子（基于取车日期：周末、节假日等）
function getCarPriceFactorByDate(dateStr) {
  if (!dateStr) return 1.0;
  const date = new Date(dateStr);
  const dayOfWeek = date.getDay();
  // 周末加价10%
  if (dayOfWeek === 0 || dayOfWeek === 6) return 1.1;
  // 简单节假日判断（示例：元旦、春节等可扩展，这里简化）
  const month = date.getMonth() + 1;
  const day = date.getDate();
  if ((month === 1 && day === 1) || (month === 5 && day === 1) || (month === 10 && day === 1)) {
    return 1.3;
  }
  return 1.0;
}

export default {
  data() {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    const defaultDate = `${year}-${month}-${day}`;
    // 明天日期
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    const tYear = tomorrow.getFullYear();
    const tMonth = String(tomorrow.getMonth() + 1).padStart(2, '0');
    const tDay = String(tomorrow.getDate()).padStart(2, '0');
    const defaultReturnDate = `${tYear}-${tMonth}-${tDay}`;
    
    return {
      currentTab: 'airplane',
      
      // 缓存
      airportCache: {},
      busStationCache: {},
      trainStationCache: {},
      geocodeCache: {},
      
      // 机票
      airDepartureInput: '',
      airArrivalInput: '',
      showDepartureSuggestions: false,
      showArrivalSuggestions: false,
      departureSuggestions: [],
      arrivalSuggestions: [],
      airplaneList: [],
      airplaneLoading: false,
      airplaneRefreshing: false,
      airplaneEmptyMsg: '',
      flightDate: defaultDate,
      minDate: defaultDate,
      
      // 火车
      trainDepartureInput: '',
      trainArrivalInput: '',
      showTrainDepartureSuggestions: false,
      showTrainArrivalSuggestions: false,
      trainDepartureSuggestions: [],
      trainArrivalSuggestions: [],
      trainList: [],
      trainLoading: false,
      trainRefreshing: false,
      trainEmptyMsg: '',
      trainDate: defaultDate,
      
      // 大巴
      busDepartureInput: '',
      busArrivalInput: '',
      showBusDepartureSuggestions: false,
      showBusArrivalSuggestions: false,
      busDepartureSuggestions: [],
      busArrivalSuggestions: [],
      busList: [],
      busLoading: false,
      busRefreshing: false,
      busEmptyMsg: '',
      busDate: defaultDate,
      
      // 租车 - 新增日期字段
      carPickupInput: '',
      showCarSuggestions: false,
      carSuggestions: [],
      carRentalList: [],
      carLoading: false,
      carRefreshing: false,
      carEmptyMsg: '',
      carPickupDate: defaultDate,      // 取车日期
      carReturnDate: defaultReturnDate, // 还车日期
      carMinDate: defaultDate,          // 最小可选日期（今天）
      
      showPermissionModal: false,
      currentLocation: { latitude: null, longitude: null, city: '' },
      searchTimeout: null
    }
  },
  
  computed: {
    formattedFlightDate() {
      if (!this.flightDate) return '请选择日期';
      const [year, month, day] = this.flightDate.split('-');
      return `${year}年${parseInt(month)}月${parseInt(day)}日`;
    },
    formattedTrainDate() {
      if (!this.trainDate) return '请选择日期';
      const [year, month, day] = this.trainDate.split('-');
      return `${year}年${parseInt(month)}月${parseInt(day)}日`;
    },
    formattedBusDate() {
      if (!this.busDate) return '请选择日期';
      const [year, month, day] = this.busDate.split('-');
      return `${year}年${parseInt(month)}月${parseInt(day)}日`;
    },
    // 租车日期格式化
    formattedCarPickupDate() {
      if (!this.carPickupDate) return '请选择日期';
      const [year, month, day] = this.carPickupDate.split('-');
      return `${year}年${parseInt(month)}月${parseInt(day)}日`;
    },
    formattedCarReturnDate() {
      if (!this.carReturnDate) return '请选择日期';
      const [year, month, day] = this.carReturnDate.split('-');
      return `${year}年${parseInt(month)}月${parseInt(day)}日`;
    },
    // 租赁天数
    rentalDays() {
      if (!this.carPickupDate || !this.carReturnDate) return 1;
      return Math.max(1, getDaysBetween(this.carPickupDate, this.carReturnDate));
    }
  },
  
  onLoad(options) {
    if (options.tab) this.currentTab = options.tab;
    this.initLocationAndLoad();
  },
  
  methods: {
    // ========== 腾讯地图 API ==========
    async requestMapAPI(url, params) {
      return new Promise((resolve, reject) => {
        const queryParams = { ...params, key: QQ_MAP_KEY, output: 'json' };
        const queryString = Object.keys(queryParams).map(k => `${k}=${encodeURIComponent(queryParams[k])}`).join('&');
        uni.request({
          url: `${QQ_MAP_API}${url}?${queryString}`,
          success: (res) => {
            if (res.data.status === 0) resolve(res.data);
            else reject(new Error(res.data.message || 'API请求失败'));
          },
          fail: reject
        });
      });
    },
    
    // 地理编码：城市名 -> 坐标
    async geocodeCity(cityName) {
      const cacheKey = `geocode_${cityName}`;
      if (this.geocodeCache[cacheKey]) return this.geocodeCache[cacheKey];
      try {
        const res = await this.requestMapAPI('/ws/geocoder/v1/', { address: cityName });
        if (res.result && res.result.location) {
          const loc = res.result.location;
          const result = { lat: loc.lat, lng: loc.lng };
          this.geocodeCache[cacheKey] = result;
          return result;
        }
        return null;
      } catch (e) {
        console.error(`地理编码失败: ${cityName}`, e);
        return null;
      }
    },
    
    // 城市建议
    async searchCitySuggestions(keyword) {
      if (!keyword || keyword.length < 2) return [];
      try {
        const res = await this.requestMapAPI('/ws/place/v1/suggestion', {
          keyword, region: '全国', region_fix: 0, get_ad: 1
        });
        return res.data.filter(item => 
          item.type === 'city' || (item.ad_info?.adcode?.toString().endsWith('00'))
        ).slice(0, 10);
      } catch (error) {
        console.error('搜索城市失败', error);
        return [];
      }
    },
    
    // 从车站名称中提取城市名（如"广州南站" -> "广州"）
    extractCityFromStationName(stationName) {
      if (!stationName) return '';
      const suffixes = ['站', '东站', '南站', '西站', '北站', '火车站', '高铁站', '城际站'];
      let city = stationName;
      for (const suffix of suffixes) {
        if (city.endsWith(suffix)) {
          city = city.slice(0, -suffix.length);
          break;
        }
      }
      return city || stationName;
    },
    
    // 检查城市是否有民用机场
    async checkCityHasAirport(rawCityName) {
      const cityName = normalizeCityName(rawCityName);
      if (!cityName) return { hasAirport: false, airportInfo: null };
      if (this.airportCache[cityName] !== undefined) return this.airportCache[cityName];
      
      const excludeKeywords = ['农庄', '餐厅', '饭馆', '路', '街', '小区', '学校', '食堂', 
                               '宾馆', '酒店', '山庄', '农家乐', '训练', '基地', '候机楼', 
                               '候机厅', '售票处', '体验馆', '展示中心', '办公楼', '停车场'];
      try {
        let res = await this.requestMapAPI('/ws/place/v1/suggestion', {
          keyword: `${cityName}机场`,
          region: cityName,
          region_fix: 1,
          page_size: 10
        });
        let airports = res.data.filter(item => {
          const title = item.title;
          if (!title.includes('机场')) return false;
          for (let kw of excludeKeywords) if (title.includes(kw)) return false;
          const category = item.category || '';
          const isAirportCategory = category === '交通设施:机场' || category === '机场' || 
                                     category.includes('机场') || category.includes('航空港');
          if (!isAirportCategory) return false;
          return title.endsWith('机场') || title.includes('国际机场');
        });
        if (airports.length === 0) {
          res = await this.requestMapAPI('/ws/place/v1/suggestion', {
            keyword: cityName,
            region: cityName,
            region_fix: 1,
            page_size: 10,
            filter: 'category=交通设施:机场'
          });
          airports = res.data.filter(item => {
            const title = item.title;
            if (!title.includes('机场')) return false;
            for (let kw of excludeKeywords) if (title.includes(kw)) return false;
            const category = item.category || '';
            const isAirportCategory = category === '交通设施:机场' || category === '机场' || category.includes('机场');
            if (!isAirportCategory) return false;
            return title.endsWith('机场') || title.includes('国际机场');
          });
        }
        if (airports.length > 0) {
          airports.sort((a, b) => a.title.length - b.title.length);
          const airport = airports[0];
          const result = { hasAirport: true, airportInfo: { name: airport.title, location: airport.location, id: airport.id } };
          this.airportCache[cityName] = result;
          return result;
        } else {
          const result = { hasAirport: false, airportInfo: null };
          this.airportCache[cityName] = result;
          return result;
        }
      } catch (error) {
        console.error(`检查${cityName}机场失败`, error);
        if (this.airportCache[cityName] === undefined) {
          this.airportCache[cityName] = { hasAirport: false, airportInfo: null };
        }
        return this.airportCache[cityName];
      }
    },
    
    // ========== 大巴汽车站识别 ==========
    async getCityBusStations(cityName) {
      const normalized = normalizeCityName(cityName);
      const cacheKey = `bus_${normalized}`;
      if (this.busStationCache[cacheKey]) return this.busStationCache[cacheKey];
      
      try {
        let keyword = `${normalized}汽车站`;
        let res = await this.requestMapAPI('/ws/place/v1/suggestion', {
          keyword: keyword,
          region: normalized,
          region_fix: 1,
          page_size: 10
        });
        let stations = res.data.filter(item => {
          const title = item.title;
          return title.includes('汽车站') && !title.includes('火车站') &&
                 (item.category === '交通设施:长途汽车站' || item.category === '交通设施:汽车站');
        }).map(item => ({ name: item.title, location: item.location, id: item.id }));
        
        if (stations.length === 0) {
          keyword = `${normalized}客运站`;
          res = await this.requestMapAPI('/ws/place/v1/suggestion', {
            keyword: keyword,
            region: normalized,
            region_fix: 1,
            page_size: 10
          });
          stations = res.data.filter(item => {
            const title = item.title;
            return (title.includes('客运站') || title.includes('汽车站')) &&
                   !title.includes('火车站') &&
                   (item.category === '交通设施:长途汽车站' || item.category === '交通设施:汽车站' || title.includes('客运站'));
          }).map(item => ({ name: item.title, location: item.location, id: item.id }));
        }
        
        if (stations.length === 0) {
          res = await this.requestMapAPI('/ws/place/v1/suggestion', {
            keyword: normalized,
            region: '全国',
            page_size: 10,
            filter: 'category=交通设施:长途汽车站'
          });
          stations = res.data.filter(item => {
            const title = item.title;
            return title.includes(normalized) && (title.includes('汽车站') || title.includes('客运站')) && !title.includes('火车站');
          }).map(item => ({ name: item.title, location: item.location, id: item.id }));
        }
        
        if (stations.length === 0) {
          keyword = `${normalized}长途汽车站`;
          res = await this.requestMapAPI('/ws/place/v1/suggestion', {
            keyword: keyword,
            region: '全国',
            page_size: 10
          });
          stations = res.data.filter(item => {
            const title = item.title;
            return (title.includes('汽车站') || title.includes('客运站')) && !title.includes('火车站');
          }).map(item => ({ name: item.title, location: item.location, id: item.id }));
        }
        
        if (stations.length === 0) {
          keyword = `${normalized}站`;
          res = await this.requestMapAPI('/ws/place/v1/suggestion', {
            keyword: keyword,
            region: '全国',
            page_size: 10
          });
          stations = res.data.filter(item => {
            const title = item.title;
            return (title.includes('汽车站') || title.includes('客运站')) && !title.includes('火车站');
          }).map(item => ({ name: item.title, location: item.location, id: item.id }));
        }
        
        if (stations.length > 0) {
          stations.sort((a, b) => a.name.length - b.name.length);
          this.busStationCache[cacheKey] = stations;
          console.log(`识别到汽车站: ${cityName} -> ${stations[0].name}`);
          return stations;
        }
        
        console.warn(`未找到${cityName}的汽车站，将使用虚拟站名：${normalized}汽车站`);
        const cityCenter = await this.geocodeCity(normalized);
        if (cityCenter) {
          const virtualStation = {
            name: `${normalized}汽车站`,
            location: cityCenter,
            id: `virtual_bus_${normalized}`
          };
          this.busStationCache[cacheKey] = [virtualStation];
          uni.showToast({
            title: `未找到真实汽车站，将使用${virtualStation.name}模拟`,
            icon: 'none',
            duration: 2000
          });
          return [virtualStation];
        }
        
        return [];
      } catch (error) {
        console.error(`获取${cityName}汽车站失败`, error);
        const cityCenter = { lat: 23.1291, lng: 113.2644 };
        const virtualStation = {
          name: `${normalized}汽车站`,
          location: cityCenter,
          id: `virtual_bus_${normalized}`
        };
        this.busStationCache[cacheKey] = [virtualStation];
        return [virtualStation];
      }
    },
    
    getBusPriceFactorByDate(dateStr) {
      if (!dateStr) return 1.0;
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const targetDate = new Date(dateStr);
      targetDate.setHours(0, 0, 0, 0);
      const diffDays = Math.ceil((targetDate - today) / (1000 * 60 * 60 * 24));
      if (diffDays < 0) return 1.0;
      if (diffDays >= 14) return 0.90;
      if (diffDays >= 7) return 0.95;
      if (diffDays >= 3) return 0.98;
      if (diffDays >= 1) return 1.0;
      return 1.03;
    },
    
    async generateBuses(depCity, arrCity, dateStr) {
      if (!depCity || !arrCity) {
        this.busEmptyMsg = '请填写完整的城市信息';
        return [];
      }
      if (depCity === arrCity) {
        this.busEmptyMsg = '出发城市和到达城市不能相同';
        return [];
      }
      
      const depStations = await this.getCityBusStations(depCity);
      const arrStations = await this.getCityBusStations(arrCity);
      
      if (depStations.length === 0) {
        this.busEmptyMsg = `未找到${depCity}的汽车站，请尝试其他城市或稍后再试`;
        return [];
      }
      if (arrStations.length === 0) {
        this.busEmptyMsg = `未找到${arrCity}的汽车站，请尝试其他城市或稍后再试`;
        return [];
      }
      
      const depStation = depStations[0];
      const arrStation = arrStations[0];
      const distance = this.getGreatCircleDistance(depStation.location, arrStation.location);
      const travelMin = this.calcBusMinutes(distance);
      const basePrice = Math.max(30, Math.round(distance * 0.35));
      const priceFactor = this.getBusPriceFactorByDate(dateStr);
      
      const busTypes = ['豪华大巴', '新能源大巴', '商务大巴', '普通大巴'];
      const buses = [];
      const busCount = Math.min(10, Math.floor(Math.random() * 6) + 5);
      
      for (let i = 0; i < busCount; i++) {
        let price = Math.round(basePrice * priceFactor) + Math.floor(Math.random() * 30) - 15;
        price = Math.max(30, price);
        const depHour = Math.floor(Math.random() * 14) + 6;
        const depMin = Math.floor(Math.random() * 60);
        let arrTotal = depHour * 60 + depMin + travelMin;
        const arrHour = Math.floor(arrTotal / 60) % 24;
        const arrMin = arrTotal % 60;
        
        buses.push({
          id: `bus_${Date.now()}_${i}_${Math.random()}`,
          departure: {
            city: depCity,
            station: depStation.name,
            time: `${String(depHour).padStart(2,'0')}:${String(depMin).padStart(2,'0')}`
          },
          arrival: {
            city: arrCity,
            station: arrStation.name,
            time: `${String(arrHour).padStart(2,'0')}:${String(arrMin).padStart(2,'0')}`
          },
          duration: formatDuration(travelMin),
          type: busTypes[Math.floor(Math.random() * busTypes.length)],
          price: price,
          availableSeats: Math.floor(Math.random() * 40) + 5,
          departureDate: formatDateMD(dateStr)
        });
      }
      buses.sort((a, b) => a.departure.time.localeCompare(b.departure.time));
      return buses;
    },
    
    async loadBusData() {
      const dep = this.busDepartureInput.trim();
      const arr = this.busArrivalInput.trim();
      const date = this.busDate;
      
      if (!dep || !arr) {
        this.busEmptyMsg = '请填写完整的城市信息';
        this.busList = [];
        return;
      }
      if (!date) {
        this.busEmptyMsg = '请选择出发日期';
        this.busList = [];
        return;
      }
      
      const normDep = normalizeCityName(dep);
      const normArr = normalizeCityName(arr);
      if (normDep === normArr) {
        this.busEmptyMsg = '出发城市和到达城市不能相同，请选择不同城市';
        this.busList = [];
        return;
      }
      
      this.busLoading = true;
      this.busEmptyMsg = '';
      this.busList = [];
      
      try {
        const buses = await this.generateBuses(dep, arr, date);
        this.busList = buses;
        if (buses.length === 0 && !this.busEmptyMsg) {
          this.busEmptyMsg = '暂无大巴班次，请尝试其他日期或城市';
        }
      } catch (err) {
        console.error('搜索大巴失败', err);
        this.busEmptyMsg = '搜索失败，请稍后重试';
      } finally {
        this.busLoading = false;
        this.busRefreshing = false;
      }
    },
    
    onBusDateChange(e) {
      const selectedDate = e.detail.value;
      if (selectedDate) {
        this.busDate = selectedDate;
        this.loadBusData();
      }
    },
    
    // ========== 火车相关方法 ==========
    async getCityCenter(cityName) {
      const coords = await this.geocodeCity(cityName);
      if (coords) return coords;
      return { lat: 39.9042, lng: 116.4074 };
    },
    
    async getMainTrainStation(cityName) {
      if (!cityName) return null;
      const normalized = normalizeCityName(cityName);
      const cacheKey = `train_main_${normalized}`;
      if (this.trainStationCache[cacheKey]) return this.trainStationCache[cacheKey];
      
      try {
        let keyword = `${normalized}站`;
        let res = await this.requestMapAPI('/ws/place/v1/suggestion', {
          keyword: keyword,
          region: '全国',
          page_size: 5
        });
        let stations = res.data.filter(item => {
          const title = item.title;
          const isTrainStation = (item.category === '交通设施:火车站') || 
                                  title.includes('火车站') ||
                                  (title.includes('站') && !title.includes('汽车站') && !title.includes('公交站'));
          return isTrainStation;
        });
        if (stations.length === 0) {
          keyword = `${normalized}火车站`;
          res = await this.requestMapAPI('/ws/place/v1/suggestion', {
            keyword: keyword,
            region: '全国',
            page_size: 5
          });
          stations = res.data.filter(item => {
            const title = item.title;
            const isTrainStation = (item.category === '交通设施:火车站') || title.includes('火车站');
            const isNotBusStation = !title.includes('汽车站') && !title.includes('公交站');
            return isTrainStation && isNotBusStation;
          });
        }
        if (stations.length === 0) {
          res = await this.requestMapAPI('/ws/place/v1/suggestion', {
            keyword: normalized,
            region: '全国',
            page_size: 10,
            filter: 'category=交通设施:火车站'
          });
          stations = res.data.filter(item => {
            const title = item.title;
            return title.includes(normalized) && 
                   !title.includes('汽车站') && !title.includes('公交站');
          });
        }
        if (stations.length === 0) {
          keyword = `${normalized}站`;
          res = await this.requestMapAPI('/ws/place/v1/suggestion', {
            keyword: keyword,
            region: '全国',
            page_size: 5
          });
          stations = res.data.filter(item => {
            const title = item.title;
            return title.includes('站') && !title.includes('汽车站') && !title.includes('公交站');
          });
        }
        if (stations.length > 0) {
          stations.sort((a, b) => a.title.length - b.title.length);
          const station = stations[0];
          const result = { name: station.title, location: station.location, id: station.id };
          this.trainStationCache[cacheKey] = result;
          console.log(`识别到车站: ${cityName} -> ${station.title}`);
          return result;
        }
        console.warn(`未找到${cityName}的火车站，将使用虚拟站名：${normalized}站`);
        const cityCenter = await this.getCityCenter(normalized);
        const virtualStation = {
          name: `${normalized}站`,
          location: { lat: cityCenter.lat, lng: cityCenter.lng },
          id: `virtual_${normalized}`
        };
        this.trainStationCache[cacheKey] = virtualStation;
        uni.showToast({
          title: `未找到真实车站，将使用${virtualStation.name}模拟`,
          icon: 'none',
          duration: 2000
        });
        return virtualStation;
      } catch (error) {
        console.error(`获取${cityName}火车站失败`, error);
        const cityCenter = await this.getCityCenter(normalized);
        return {
          name: `${normalized}站`,
          location: { lat: cityCenter.lat, lng: cityCenter.lng },
          id: `virtual_${normalized}`
        };
      }
    },
    
    async searchTrainStations(keyword) {
      if (!keyword || keyword.length < 1) return [];
      try {
        const res = await this.requestMapAPI('/ws/place/v1/suggestion', {
          keyword: keyword,
          region: '全国',
          page_size: 10,
          filter: 'category=交通设施:火车站'
        });
        const stations = res.data.filter(item => {
          const title = item.title;
          return (item.category === '交通设施:火车站' || title.includes('火车站')) &&
                 !title.includes('汽车站') && !title.includes('公交站');
        }).slice(0, 8);
        return stations;
      } catch (error) {
        console.error('搜索火车站失败', error);
        return [];
      }
    },
    
    async resolveTrainStation(input) {
      if (!input || !input.trim()) return null;
      const trimmed = input.trim();
      const cacheKey = `train_resolve_${trimmed}`;
      if (this.trainStationCache[cacheKey]) return this.trainStationCache[cacheKey];
      try {
        const res = await this.requestMapAPI('/ws/place/v1/suggestion', {
          keyword: trimmed,
          region: '全国',
          page_size: 3,
          filter: 'category=交通设施:火车站'
        });
        let matched = res.data.find(item => 
          item.title === trimmed && 
          (item.category === '交通设施:火车站' || item.title.includes('火车站'))
        );
        if (!matched && res.data.length > 0) {
          matched = res.data[0];
        }
        if (matched) {
          const result = { name: matched.title, location: matched.location, id: matched.id };
          this.trainStationCache[cacheKey] = result;
          return result;
        }
      } catch (e) {
        console.warn(`直接搜索车站失败: ${trimmed}`, e);
      }
      const station = await this.getMainTrainStation(trimmed);
      if (station) {
        this.trainStationCache[cacheKey] = station;
      }
      return station;
    },
    
    getTrainPriceFactorByDate(dateStr) {
      if (!dateStr) return 1.0;
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const targetDate = new Date(dateStr);
      targetDate.setHours(0, 0, 0, 0);
      const diffDays = Math.ceil((targetDate - today) / (1000 * 60 * 60 * 24));
      if (diffDays < 0) return 1.0;
      if (diffDays >= 14) return 0.85;
      if (diffDays >= 7) return 0.92;
      if (diffDays >= 3) return 0.98;
      if (diffDays >= 1) return 1.0;
      return 1.05;
    },
    
    async generateTrainsWithStations(depStation, arrStation, dateStr) {
      if (!depStation || !arrStation) {
        this.trainEmptyMsg = '请填写完整的出发站和到达站';
        return [];
      }
      if (depStation.name === arrStation.name) {
        this.trainEmptyMsg = '出发站和到达站不能相同';
        return [];
      }
      const distance = this.getGreatCircleDistance(depStation.location, arrStation.location);
      const basePrice = Math.max(50, Math.round(distance * 0.45));
      const priceFactor = this.getTrainPriceFactorByDate(dateStr);
      const trainTypes = [
        { prefix: 'G', name: '高铁', price: Math.round(basePrice * priceFactor), speed: 300 },
        { prefix: 'D', name: '动车', price: Math.round((basePrice - 10) * priceFactor), speed: 250 },
        { prefix: 'C', name: '城际', price: Math.round((basePrice - 5) * priceFactor), speed: 200 },
        { prefix: 'K', name: '快速', price: Math.round((basePrice - 30) * priceFactor), speed: 120 },
        { prefix: 'T', name: '特快', price: Math.round((basePrice - 20) * priceFactor), speed: 140 }
      ];
      const trains = [];
      const trainCount = Math.min(10, Math.floor(Math.random() * 6) + 5);
      for (let i = 0; i < trainCount; i++) {
        const tt = trainTypes[Math.floor(Math.random() * trainTypes.length)];
        const trainNum = Math.floor(Math.random() * 9000) + 1000;
        const depHour = Math.floor(Math.random() * 20) + 6;
        const depMin = Math.floor(Math.random() * 60);
        const travelMin = this.calcTrainMinutes(distance, tt.speed);
        let arrTotal = depHour * 60 + depMin + travelMin;
        const arrHour = Math.floor(arrTotal / 60) % 24;
        const arrMin = arrTotal % 60;
        trains.push({
          id: `train_${Date.now()}_${i}_${Math.random()}`,
          trainNumber: `${tt.prefix}${trainNum}`,
          type: tt.name,
          price: Math.max(30, tt.price),
          departure: { 
            station: depStation.name, 
            time: `${String(depHour).padStart(2,'0')}:${String(depMin).padStart(2,'0')}` 
          },
          arrival: { 
            station: arrStation.name, 
            time: `${String(arrHour).padStart(2,'0')}:${String(arrMin).padStart(2,'0')}` 
          },
          duration: formatDuration(travelMin),
          departureDate: formatDateMD(dateStr),
          availableSeats: [
            { type: '二等座', count: Math.floor(Math.random() * 150) + 20 },
            { type: '一等座', count: Math.floor(Math.random() * 80) + 10 },
            { type: '商务座', count: Math.floor(Math.random() * 20) + 2 },
            { type: '无座', count: Math.floor(Math.random() * 100) + 30 }
          ]
        });
      }
      trains.sort((a, b) => a.departure.time.localeCompare(b.departure.time));
      return trains;
    },
    
    async loadTrainData() {
      const depInput = this.trainDepartureInput.trim();
      const arrInput = this.trainArrivalInput.trim();
      if (!depInput || !arrInput) {
        this.trainEmptyMsg = '请填写完整的出发站/城市和到达站/城市';
        this.trainList = [];
        return;
      }
      if (!this.trainDate) {
        this.trainEmptyMsg = '请选择出发日期';
        this.trainList = [];
        return;
      }
      
      const depCityFromStation = this.extractCityFromStationName(depInput);
      const arrCityFromStation = this.extractCityFromStationName(arrInput);
      const normDepCity = normalizeCityName(depCityFromStation);
      const normArrCity = normalizeCityName(arrCityFromStation);
      
      if (normDepCity && normArrCity && normDepCity === normArrCity) {
        this.trainEmptyMsg = '出发地和到达地不能为同一城市，请选择不同城市';
        this.trainList = [];
        return;
      }
      
      this.trainLoading = true;
      this.trainEmptyMsg = '';
      this.trainList = [];
      try {
        const [depStation, arrStation] = await Promise.all([
          this.resolveTrainStation(depInput),
          this.resolveTrainStation(arrInput)
        ]);
        if (!depStation) {
          this.trainEmptyMsg = `无法识别出发站“${depInput}”，请尝试输入城市名（如：北京、上海）或具体站名（如：广州南）`;
          this.trainLoading = false;
          return;
        }
        if (!arrStation) {
          this.trainEmptyMsg = `无法识别到达站“${arrInput}”，请尝试输入城市名（如：北京、上海）或具体站名（如：广州南）`;
          this.trainLoading = false;
          return;
        }
        
        const depStationCity = this.extractCityFromStationName(depStation.name);
        const arrStationCity = this.extractCityFromStationName(arrStation.name);
        if (normalizeCityName(depStationCity) === normalizeCityName(arrStationCity)) {
          this.trainEmptyMsg = '出发站和到达站不能在同一城市，请选择不同城市的车站';
          this.trainList = [];
          this.trainLoading = false;
          return;
        }
        
        const trains = await this.generateTrainsWithStations(depStation, arrStation, this.trainDate);
        this.trainList = trains;
        if (trains.length === 0 && !this.trainEmptyMsg) {
          this.trainEmptyMsg = '暂无车次，请尝试其他日期或车站';
        }
      } catch (err) {
        console.error('搜索车次失败', err);
        this.trainEmptyMsg = '搜索失败，请稍后重试';
      } finally {
        this.trainLoading = false;
        this.trainRefreshing = false;
      }
    },
    
    onTrainDateChange(e) {
      const selectedDate = e.detail.value;
      if (selectedDate) {
        this.trainDate = selectedDate;
        this.loadTrainData();
      }
    },
    
    // ========== 距离与时间计算核心 ==========
    getGreatCircleDistance(loc1, loc2) {
      return haversineDistance(loc1.lat, loc1.lng, loc2.lat, loc2.lng);
    },
    
    calcFlightMinutes(distanceKm) {
      return Math.round((distanceKm / 850) * 60 + 30);
    },
    
    calcTrainMinutes(distanceKm, speedKmh) {
      return Math.round((distanceKm * 1.2 / speedKmh) * 60);
    },
    
    calcBusMinutes(distanceKm) {
      return Math.round((distanceKm * 1.3 / 80) * 60);
    },
    
    // ========== 机票业务 ==========
    getFlightPriceFactorByDate(dateStr) {
      if (!dateStr) return 1.0;
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const targetDate = new Date(dateStr);
      targetDate.setHours(0, 0, 0, 0);
      const diffDays = Math.ceil((targetDate - today) / (1000 * 60 * 60 * 24));
      if (diffDays < 0) return 1.0;
      if (diffDays >= 14) return 0.80;
      if (diffDays >= 7) return 0.88;
      if (diffDays >= 3) return 0.95;
      if (diffDays >= 1) return 1.0;
      return 1.08;
    },
    
    async generateFlights(rawDepartureCity, rawArrivalCity, dateStr) {
      const departureCity = normalizeCityName(rawDepartureCity);
      const arrivalCity = normalizeCityName(rawArrivalCity);
      if (!departureCity || !arrivalCity) {
        this.airplaneEmptyMsg = '请填写完整的城市信息';
        return [];
      }
      if (departureCity === arrivalCity) {
        this.airplaneEmptyMsg = '出发城市和到达城市不能相同';
        return [];
      }
      const depCheck = await this.checkCityHasAirport(departureCity);
      if (!depCheck.hasAirport) {
        this.airplaneEmptyMsg = `出发城市“${rawDepartureCity}”没有民用机场，请选择其他城市`;
        return [];
      }
      const arrCheck = await this.checkCityHasAirport(arrivalCity);
      if (!arrCheck.hasAirport) {
        this.airplaneEmptyMsg = `到达城市“${rawArrivalCity}”没有民用机场，请选择其他城市`;
        return [];
      }
      const depAirport = depCheck.airportInfo;
      const arrAirport = arrCheck.airportInfo;
      const distance = this.getGreatCircleDistance(depAirport.location, arrAirport.location);
      if (distance < 100) {
        this.airplaneEmptyMsg = '两地距离过近（小于100公里），建议选择高铁出行';
        return [];
      }
      const flightMinutes = this.calcFlightMinutes(distance);
      const flights = [];
      const flightCount = Math.min(6, Math.floor(Math.random() * 4) + 3);
      const basePrice = Math.round(distance * 0.8 + 100);
      const dateFactor = this.getFlightPriceFactorByDate(dateStr);
      for (let i = 0; i < flightCount; i++) {
        const randomDiscount = 0.6 + Math.random() * 0.4;
        let price = Math.round(basePrice * randomDiscount * dateFactor);
        price = Math.max(300, Math.min(2500, price));
        const airline = airlines[Math.floor(Math.random() * airlines.length)];
        const flightNum = Math.floor(Math.random() * 9000) + 1000;
        const depHour = Math.floor(Math.random() * 16) + 6;
        const depMin = Math.floor(Math.random() * 60);
        let arrTotal = depHour * 60 + depMin + flightMinutes;
        const arrHour = Math.floor(arrTotal / 60) % 24;
        const arrMin = arrTotal % 60;
        let discountTag = '';
        const discountPercent = Math.round(randomDiscount * 100);
        if (randomDiscount < 0.7) discountTag = `${discountPercent}折`;
        else if (dateFactor < 0.9) discountTag = `早鸟${Math.round(dateFactor*100)}折`;
        flights.push({
          id: `flight_${Date.now()}_${i}_${Math.random()}`,
          departureDate: formatDateMD(dateStr),
          departure: {
            city: rawDepartureCity,
            airport: depAirport.name,
            time: `${String(depHour).padStart(2, '0')}:${String(depMin).padStart(2, '0')}`
          },
          arrival: {
            city: rawArrivalCity,
            airport: arrAirport.name,
            time: `${String(arrHour).padStart(2, '0')}:${String(arrMin).padStart(2, '0')}`
          },
          duration: formatDuration(flightMinutes),
          airline: airline.name,
          flightNumber: `${airline.code}${flightNum}`,
          price: price,
          type: Math.random() > 0.2 ? '直达' : (Math.random() > 0.5 ? '经停' : '中转'),
          discount: discountTag
        });
      }
      flights.sort((a, b) => a.departure.time.localeCompare(b.departure.time));
      return flights;
    },
    
    async loadAirplaneData() {
      const depCity = this.airDepartureInput.trim();
      const arrCity = this.airArrivalInput.trim();
      if (!depCity || !arrCity) {
        this.airplaneEmptyMsg = '请填写完整的城市信息';
        this.airplaneList = [];
        return;
      }
      if (!this.flightDate) {
        this.airplaneEmptyMsg = '请选择出发日期';
        this.airplaneList = [];
        return;
      }
      
      const normDep = normalizeCityName(depCity);
      const normArr = normalizeCityName(arrCity);
      if (normDep === normArr) {
        this.airplaneEmptyMsg = '出发城市和到达城市不能相同，请选择不同城市';
        this.airplaneList = [];
        return;
      }
      
      this.airplaneLoading = true;
      this.airplaneEmptyMsg = '';
      this.airplaneList = [];
      try {
        const flights = await this.generateFlights(depCity, arrCity, this.flightDate);
        this.airplaneList = flights;
        if (flights.length === 0 && !this.airplaneEmptyMsg) {
          this.airplaneEmptyMsg = '暂无航班，请选择其他城市';
        }
      } catch (err) {
        console.error('搜索航班失败', err);
        this.airplaneEmptyMsg = '搜索失败，请稍后重试';
      } finally {
        this.airplaneLoading = false;
        this.airplaneRefreshing = false;
      }
    },
    
    onFlightDateChange(e) {
      const selectedDate = e.detail.value;
      if (selectedDate) {
        this.flightDate = selectedDate;
        this.loadAirplaneData();
      }
    },
    
    // ========== 租车业务（修改为支持日期选择） ==========
    // 生成租车公司列表，基于城市、取车日期、还车日期
    generateCarRentals(city, pickupDate, returnDate) {
      if (!city) {
        this.carEmptyMsg = '请输入城市名称';
        return [];
      }
      if (!pickupDate || !returnDate) {
        this.carEmptyMsg = '请选择取车日期和还车日期';
        return [];
      }
      
      const days = getDaysBetween(pickupDate, returnDate);
      if (days < 1) {
        this.carEmptyMsg = '还车日期必须晚于取车日期';
        return [];
      }
      
      const dateFactor = getCarPriceFactorByDate(pickupDate);
      const cityHash = city.split('').reduce((a, b) => a + b.charCodeAt(0), 0);
      const cityPriceFactor = 0.6 + (cityHash % 10) * 0.1;
      
      return carRentalCompanies.map((company, idx) => {
        // 基础日均价
        const baseDailyPrice = Math.floor(100 * cityPriceFactor * dateFactor);
        // 总价 = 日均价 * 天数（再加一点随机波动）
        const totalStartingPrice = Math.floor(baseDailyPrice * days * (0.9 + Math.random() * 0.2));
        const dailyStartingPrice = Math.floor(totalStartingPrice / days);
        
        // 生成热门车型（带日单价和总价）
        const shuffled = [...carModels].sort(() => 0.5 - Math.random());
        const popularModels = shuffled.slice(0, 3).map(m => {
          const dailyPrice = Math.floor(m.basePrice * cityPriceFactor * dateFactor * (0.8 + Math.random() * 0.4));
          const totalPrice = dailyPrice * days;
          return {
            name: m.name,
            dailyPrice: dailyPrice,
            totalPrice: totalPrice
          };
        });
        
        return {
          id: `car_${Date.now()}_${idx}`,
          name: company.name,
          rating: (company.rating + (Math.random() * 0.3 - 0.15)).toFixed(1),
          totalStartingPrice: totalStartingPrice,
          dailyStartingPrice: dailyStartingPrice,
          popularModels,
          features: company.features,
          rentalDays: days
        };
      });
    },
    
    // 校验并修正租车日期
    validateCarDates() {
      if (!this.carPickupDate) {
        this.carPickupDate = this.minDate;
      }
      if (!this.carReturnDate) {
        const tomorrow = new Date(this.carPickupDate);
        tomorrow.setDate(tomorrow.getDate() + 1);
        const tYear = tomorrow.getFullYear();
        const tMonth = String(tomorrow.getMonth() + 1).padStart(2, '0');
        const tDay = String(tomorrow.getDate()).padStart(2, '0');
        this.carReturnDate = `${tYear}-${tMonth}-${tDay}`;
      }
      if (this.carReturnDate < this.carPickupDate) {
        this.carReturnDate = this.carPickupDate;
        const nextDay = new Date(this.carReturnDate);
        nextDay.setDate(nextDay.getDate() + 1);
        const nYear = nextDay.getFullYear();
        const nMonth = String(nextDay.getMonth() + 1).padStart(2, '0');
        const nDay = String(nextDay.getDate()).padStart(2, '0');
        this.carReturnDate = `${nYear}-${nMonth}-${nDay}`;
      }
    },
    
    async loadCarData() {
      const city = this.carPickupInput.trim();
      if (!city) {
        this.carEmptyMsg = '请输入城市名称';
        this.carRentalList = [];
        return;
      }
      this.validateCarDates();
      const pickupDate = this.carPickupDate;
      const returnDate = this.carReturnDate;
      const days = getDaysBetween(pickupDate, returnDate);
      if (days < 1) {
        this.carEmptyMsg = '还车日期必须晚于取车日期';
        this.carRentalList = [];
        return;
      }
      
      this.carLoading = true;
      this.carEmptyMsg = '';
      this.carRentalList = [];
      setTimeout(() => {
        const rentals = this.generateCarRentals(city, pickupDate, returnDate);
        this.carRentalList = rentals;
        if (rentals.length === 0) this.carEmptyMsg = '暂无租车公司';
        this.carLoading = false;
        this.carRefreshing = false;
      }, 500);
    },
    
    onCarPickupDateChange(e) {
      const selectedDate = e.detail.value;
      if (selectedDate) {
        this.carPickupDate = selectedDate;
        // 确保还车日期不早于取车日期
        if (this.carReturnDate < this.carPickupDate) {
          this.carReturnDate = this.carPickupDate;
          const nextDay = new Date(this.carReturnDate);
          nextDay.setDate(nextDay.getDate() + 1);
          const nYear = nextDay.getFullYear();
          const nMonth = String(nextDay.getMonth() + 1).padStart(2, '0');
          const nDay = String(nextDay.getDate()).padStart(2, '0');
          this.carReturnDate = `${nYear}-${nMonth}-${nDay}`;
        }
        this.loadCarData();
      }
    },
    
    onCarReturnDateChange(e) {
      const selectedDate = e.detail.value;
      if (selectedDate) {
        if (selectedDate < this.carPickupDate) {
          uni.showToast({ title: '还车日期不能早于取车日期', icon: 'none' });
          return;
        }
        this.carReturnDate = selectedDate;
        this.loadCarData();
      }
    },
    
    // ========== 通用交互 ==========
    onCityInput(type, value) {
      if (this.searchTimeout) clearTimeout(this.searchTimeout);
      this.searchTimeout = setTimeout(async () => {
        if (!value || value.length < 2) {
          if (type === 'departure') this.departureSuggestions = [];
          else if (type === 'arrival') this.arrivalSuggestions = [];
          else if (type === 'busDeparture') this.busDepartureSuggestions = [];
          else if (type === 'busArrival') this.busArrivalSuggestions = [];
          else if (type === 'car') this.carSuggestions = [];
          return;
        }
        const suggestions = await this.searchCitySuggestions(value);
        if (type === 'departure') this.departureSuggestions = suggestions;
        else if (type === 'arrival') this.arrivalSuggestions = suggestions;
        else if (type === 'busDeparture') this.busDepartureSuggestions = suggestions;
        else if (type === 'busArrival') this.busArrivalSuggestions = suggestions;
        else if (type === 'car') this.carSuggestions = suggestions;
      }, 300);
    },
    
    onTrainStationInput(type) {
      if (this.searchTimeout) clearTimeout(this.searchTimeout);
      this.searchTimeout = setTimeout(async () => {
        const value = type === 'departure' ? this.trainDepartureInput : this.trainArrivalInput;
        if (!value || value.length < 2) {
          if (type === 'departure') this.trainDepartureSuggestions = [];
          else this.trainArrivalSuggestions = [];
          return;
        }
        const stations = await this.searchTrainStations(value);
        if (type === 'departure') {
          this.trainDepartureSuggestions = stations;
        } else {
          this.trainArrivalSuggestions = stations;
        }
      }, 300);
    },
    
    selectDepartureCity(city) { this.airDepartureInput = city.name; this.showDepartureSuggestions = false; this.departureSuggestions = []; },
    selectArrivalCity(city) { this.airArrivalInput = city.name; this.showArrivalSuggestions = false; this.arrivalSuggestions = []; },
    selectTrainDepartureStation(station) { 
      this.trainDepartureInput = station.title; 
      this.showTrainDepartureSuggestions = false;
      this.trainDepartureSuggestions = [];
    },
    selectTrainArrivalStation(station) { 
      this.trainArrivalInput = station.title; 
      this.showTrainArrivalSuggestions = false;
      this.trainArrivalSuggestions = [];
    },
    selectBusDepartureCity(city) { this.busDepartureInput = city.name; this.showBusDepartureSuggestions = false; },
    selectBusArrivalCity(city) { this.busArrivalInput = city.name; this.showBusArrivalSuggestions = false; },
    selectCarCity(city) { this.carPickupInput = city.name; this.showCarSuggestions = false; this.loadCarData(); },
    
    hideSuggestionsDelayed(field) {
      setTimeout(() => {
        if (field === 'departure') this.showDepartureSuggestions = false;
        else if (field === 'arrival') this.showArrivalSuggestions = false;
        else if (field === 'trainDeparture') this.showTrainDepartureSuggestions = false;
        else if (field === 'trainArrival') this.showTrainArrivalSuggestions = false;
        else if (field === 'busDeparture') this.showBusDepartureSuggestions = false;
        else if (field === 'busArrival') this.showBusArrivalSuggestions = false;
        else if (field === 'car') this.showCarSuggestions = false;
      }, 200);
    },
    
    onCityInputFocus() {},
    
    // ========== 定位 ==========
    async initLocationAndLoad() {
      try {
        const loc = await new Promise((res, rej) => uni.getLocation({ type: 'gcj02', success: res, fail: rej }));
        this.currentLocation = { latitude: loc.latitude, longitude: loc.longitude };
        const geo = await this.requestMapAPI('/ws/geocoder/v1/', { location: `${loc.latitude},${loc.longitude}` });
        let city = geo.result?.address_component?.city || geo.result?.address_component?.district;
        if (city) {
          this.airDepartureInput = city;
          this.busDepartureInput = city;
          this.carPickupInput = city;
          this.trainDepartureInput = city;
        }
      } catch (err) {
        console.error('定位失败', err);
        try {
          const ipRes = await this.requestMapAPI('/ws/location/v1/ip', {});
          const city = ipRes.result?.ad_info?.city;
          if (city) {
            this.airDepartureInput = city;
            this.busDepartureInput = city;
            this.carPickupInput = city;
            this.trainDepartureInput = city;
          }
        } catch (e) {}
      }
      this.loadDataForCurrentTab();
    },
    
    loadDataForCurrentTab() {
      const map = { airplane: this.loadAirplaneData, train: this.loadTrainData, bus: this.loadBusData, car: this.loadCarData };
      if (map[this.currentTab]) map[this.currentTab].call(this);
    },
    
    switchTab(tab) { this.currentTab = tab; this.loadDataForCurrentTab(); },
    searchAirplane() { this.loadAirplaneData(); },
    onRefreshAirplane() { this.airplaneRefreshing = true; this.loadAirplaneData(); },
    swapAirportCities() { [this.airDepartureInput, this.airArrivalInput] = [this.airArrivalInput, this.airDepartureInput]; this.loadAirplaneData(); },
    searchTrain() { this.loadTrainData(); },
    onRefreshTrain() { this.trainRefreshing = true; this.loadTrainData(); },
    swapTrainStations() { 
      [this.trainDepartureInput, this.trainArrivalInput] = [this.trainArrivalInput, this.trainDepartureInput];
      this.loadTrainData();
    },
    searchBus() { this.loadBusData(); },
    onRefreshBus() { this.busRefreshing = true; this.loadBusData(); },
    swapBusCities() { 
      [this.busDepartureInput, this.busArrivalInput] = [this.busArrivalInput, this.busDepartureInput];
      this.loadBusData();
    },
    searchCar() { this.loadCarData(); },
    onRefreshCar() { this.carRefreshing = true; this.loadCarData(); },
    viewFlightDetail(flight) { uni.navigateTo({ url: `/pages/transport/flight-detail?id=${flight.id}` }); },
    viewTrainDetail(item) { uni.navigateTo({ url: `/pages/transport/train-detail?id=${item.id}` }); },
    viewBusDetail(item) { uni.navigateTo({ url: `/pages/transport/bus-detail?id=${item.id}` }); },
    viewCarRentalDetail(item) { uni.navigateTo({ url: `/pages/transport/car-rental-detail?id=${item.id}` }); },
    navigateToBusPage() { uni.navigateTo({ url: `/pages/bus/bus` }); },
    hidePermissionModal() { this.showPermissionModal = false; },
    requestLocationPermission() {
      this.hidePermissionModal();
      uni.openSetting({ success: (res) => {
        if (res.authSetting['scope.userLocation']) {
          uni.showToast({ title: '权限已开启，重新定位', icon: 'success' });
          setTimeout(() => this.initLocationAndLoad(), 1000);
        }
      } });
    }
  }
}
</script>

<style scoped>
.transport-page { height: 100vh; background: linear-gradient(135deg, #f0f6ff 0%, #e8ecff 100%); display: flex; flex-direction: column; }
.nav-bar { display: flex; background-color: #fff; border-bottom: 1rpx solid #e0e8ff; position: sticky; top: 0; z-index: 10; box-shadow: 0 2rpx 10rpx rgba(184,212,255,0.2); }
.nav-item { flex: 1; text-align: center; padding: 25rpx 0; position: relative; transition: all 0.3s ease; }
.nav-text { font-size: 26rpx; color: #8a9bc1; font-weight: 500; transition: all 0.3s; }
.nav-item.active .nav-text { color: #5a7bdb; font-weight: 600; }
.nav-item.active::after { content: ''; position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); width: 60rpx; height: 6rpx; background: linear-gradient(90deg, #b8d4ff, #bcc4e8); border-radius: 3rpx; box-shadow: 0 2rpx 6rpx rgba(184,212,255,0.5); }
.content-section { flex: 1; overflow: hidden; }
.tab-content { height: 100%; }
.content-scroll { height: 100%; }
.city-selector-bar { display: flex; align-items: center; justify-content: space-between; background: #fff; padding: 30rpx; border-bottom: 1rpx solid #e0e8ff; }
.city-selector-bar.single { justify-content: center; }
.city-select-item { flex: 1; position: relative; }
.city-select-item.full { width: 100%; }
.city-label { font-size: 24rpx; color: #8a9bc1; display: block; margin-bottom: 8rpx; }
.input-wrapper { position: relative; }
.city-input { background: #f0f7ff; border: 1rpx solid #d0deff; border-radius: 40rpx; height: 80rpx; line-height: 80rpx; padding: 0 25rpx; font-size: 28rpx; color: #3a5bc7; width: 100%; box-sizing: border-box; }
.suggestions-list { position: absolute; top: 100%; left: 0; right: 0; background: white; border: 1rpx solid #e0e8ff; border-radius: 16rpx; max-height: 300rpx; overflow-y: auto; z-index: 20; box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.1); }
.suggestion-item { padding: 20rpx 25rpx; font-size: 26rpx; color: #3a5bc7; border-bottom: 1rpx solid #f0f0f0; }
.suggestion-item:active { background: #e8ecff; }
.city-swap { padding: 20rpx; }
.swap-icon { width: 50rpx; height: 50rpx; }
.date-selector-bar { display: flex; align-items: center; justify-content: space-between; background: #fff; padding: 20rpx 30rpx; border-bottom: 1rpx solid #e0e8ff; margin-top: 2rpx; }
.date-selector-bar.dual { display: flex; gap: 30rpx; justify-content: space-between; }
.date-selector-bar.dual .date-item { flex: 1; display: flex; align-items: center; justify-content: space-between; }
.date-label { font-size: 26rpx; color: #3a5bc7; font-weight: 500; }
.date-picker-display { background: #f0f7ff; border: 1rpx solid #d0deff; border-radius: 40rpx; padding: 15rpx 30rpx; font-size: 28rpx; color: #3a5bc7; min-width: 200rpx; text-align: center; }
.search-btn { margin: 30rpx; background: linear-gradient(135deg, #5a7bdb, #3a5bc7); border-radius: 50rpx; padding: 25rpx; text-align: center; }
.search-btn-text { color: #fff; font-size: 32rpx; font-weight: 600; }
.flight-list, .train-list, .bus-list, .car-rental-list { padding: 0 30rpx 30rpx; }
.flight-card, .train-card, .bus-card, .car-rental-card { background: linear-gradient(135deg, #ffffff 0%, #f8fbff 100%); border-radius: 20rpx; padding: 30rpx; margin-top: 25rpx; box-shadow: 0 4rpx 15rpx rgba(184,212,255,0.3); border: 1rpx solid #e0e8ff; transition: all 0.3s ease; }
.flight-card:active, .train-card:active, .bus-card:active, .car-rental-card:active { transform: translateY(4rpx); box-shadow: 0 2rpx 8rpx rgba(184,212,255,0.2); }
.flight-header, .train-header, .bus-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25rpx; flex-wrap: wrap; gap: 10rpx; }
.flight-route, .bus-route { display: flex; align-items: center; gap: 15rpx; }
.city { font-size: 32rpx; font-weight: 600; color: #3a5bc7; }
.route-arrow { width: 40rpx; height: 40rpx; }
.flight-date-wrapper { background: #e8ecff; border-radius: 20rpx; padding: 6rpx 16rpx; }
.flight-date-text { font-size: 24rpx; color: #5a7bdb; font-weight: 500; }
.flight-price, .train-price, .bus-price { text-align: right; }
.price { font-size: 36rpx; color: #ff6b6b; font-weight: 700; }
.price-desc { font-size: 22rpx; color: #8a9bc1; margin-left: 5rpx; }
.flight-detail, .train-route, .bus-detail { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20rpx; }
.time-section { text-align: center; flex: 1; }
.time { font-size: 28rpx; font-weight: 600; color: #3a5bc7; display: block; }
.airport, .station { font-size: 22rpx; color: #8a9bc1; display: block; margin-top: 5rpx; }
.duration-section { text-align: center; flex: 2; }
.duration { font-size: 24rpx; color: #8a9bc1; display: block; margin-bottom: 10rpx; }
.flight-line, .route-line { display: flex; align-items: center; justify-content: center; margin: 10rpx 0; }
.line-dot { width: 12rpx; height: 12rpx; border-radius: 50%; background: #5a7bdb; }
.line { flex: 1; height: 2rpx; background: #d0deff; margin: 0 10rpx; }
.flight-type { font-size: 22rpx; color: #66bb6a; background: #f0fff0; padding: 5rpx 10rpx; border-radius: 10rpx; }
.flight-footer, .bus-footer { display: flex; justify-content: space-between; align-items: center; padding-top: 20rpx; border-top: 1rpx solid #e0e8ff; }
.airline, .flight-number, .bus-type { font-size: 24rpx; color: #8a9bc1; }
.discount-tag { background: linear-gradient(135deg, #ff6b6b, #ff8e8e); color: #fff; padding: 8rpx 16rpx; border-radius: 15rpx; font-size: 22rpx; font-weight: 600; }
.train-info { display: flex; align-items: center; gap: 15rpx; }
.train-number { font-size: 28rpx; font-weight: 600; color: #3a5bc7; }
.train-type { background: linear-gradient(135deg, #b8d4ff, #bcc4e8); color: #3a5bc7; padding: 5rpx 12rpx; border-radius: 12rpx; font-size: 22rpx; font-weight: 600; }
.train-seats { display: flex; gap: 15rpx; margin-top: 15rpx; flex-wrap: wrap; }
.seat-item { background: #f0f7ff; color: #5a7bdb; padding: 8rpx 15rpx; border-radius: 12rpx; font-size: 22rpx; }
.seats-available { font-size: 24rpx; color: #66bb6a; }
.train-date-info { margin-top: 12rpx; text-align: center; }
.train-date-info .date-text { font-size: 22rpx; color: #8a9bc1; background: #e8ecff; padding: 4rpx 12rpx; border-radius: 20rpx; }
.bus-date-info { margin-top: 12rpx; text-align: center; }
.bus-date-info .date-text { font-size: 22rpx; color: #8a9bc1; background: #e8ecff; padding: 4rpx 12rpx; border-radius: 20rpx; }
.company-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 25rpx; }
.company-info { flex: 1; }
.company-name { font-size: 28rpx; font-weight: 600; color: #3a5bc7; display: block; margin-bottom: 8rpx; }
.company-rating { font-size: 24rpx; color: #ff9500; }
.starting-price { text-align: right; }
.starting-price .price { font-size: 32rpx; }
.starting-price .daily-price { font-size: 20rpx; color: #8a9bc1; display: block; margin-top: 4rpx; }
.car-models { margin-bottom: 20rpx; }
.models-scroll { white-space: nowrap; }
.car-model { display: inline-flex; flex-direction: column; align-items: center; margin-right: 25rpx; text-align: center; width: 160rpx; }
.model-name { font-size: 24rpx; color: #3a5bc7; font-weight: 500; margin-bottom: 5rpx; }
.model-daily-price { font-size: 20rpx; color: #66bb6a; }
.model-total-price { font-size: 22rpx; color: #ff6b6b; font-weight: 600; margin-top: 4rpx; }
.company-features { display: flex; flex-wrap: wrap; gap: 15rpx; margin-top: 15rpx; }
.feature-tag { background: linear-gradient(135deg, #f0f7ff, #e8ecff); color: #5a7bdb; padding: 8rpx 16rpx; border-radius: 15rpx; font-size: 22rpx; border: 1rpx solid #d0deff; }
.rental-days { font-size: 22rpx; color: #8a9bc1; margin-top: 12rpx; text-align: center; background: #e8ecff; display: inline-block; padding: 6rpx 16rpx; border-radius: 20rpx; }
.public-transport-entry { padding: 30rpx; }
.entry-header { text-align: center; margin-bottom: 40rpx; }
.entry-title { font-size: 36rpx; color: #3a5bc7; font-weight: 700; display: block; margin-bottom: 15rpx; }
.entry-desc { font-size: 26rpx; color: #8a9bc1; line-height: 1.5; }
.entry-cards { margin-bottom: 40rpx; }
.entry-card { display: flex; align-items: center; background: linear-gradient(135deg, #ffffff 0%, #f8fbff 100%); border-radius: 20rpx; padding: 30rpx; margin-bottom: 25rpx; box-shadow: 0 4rpx 15rpx rgba(184,212,255,0.3); border: 1rpx solid #e0e8ff; }
.entry-card:active { transform: translateY(4rpx); }
.entry-card.bus { border-left: 6rpx solid #b8d4ff; }
.entry-card.subway { border-left: 6rpx solid #ff9500; }
.entry-card.route { border-left: 6rpx solid #66bb6a; }
.card-icon { width: 80rpx; height: 80rpx; background: linear-gradient(135deg, #f0f7ff, #e8ecff); border-radius: 20rpx; display: flex; align-items: center; justify-content: center; margin-right: 25rpx; }
.card-icon image { width: 50rpx; height: 50rpx; }
.card-content { flex: 1; }
.card-title { font-size: 32rpx; color: #3a5bc7; font-weight: 600; display: block; margin-bottom: 8rpx; }
.card-desc { font-size: 24rpx; color: #8a9bc1; }
.card-arrow { width: 40rpx; height: 40rpx; }
.card-arrow image { width: 24rpx; height: 24rpx; }
.quick-action { background: linear-gradient(135deg, #ffffff 0%, #f8fbff 100%); border-radius: 20rpx; padding: 30rpx; box-shadow: 0 4rpx 15rpx rgba(184,212,255,0.3); border: 1rpx solid #e0e8ff; }
.action-title { font-size: 28rpx; color: #3a5bc7; font-weight: 600; display: block; margin-bottom: 25rpx; text-align: center; }
.action-buttons { display: flex; justify-content: space-around; }
.action-btn { display: flex; flex-direction: column; align-items: center; gap: 15rpx; padding: 20rpx; }
.action-btn:active { transform: scale(0.95); }
.action-icon { width: 60rpx; height: 60rpx; }
.action-btn text { font-size: 24rpx; color: #5a7bdb; font-weight: 500; }
.loading-container, .empty-container { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 100rpx 0; }
.loading-text, .empty-text { font-size: 28rpx; color: #999; }
.permission-modal { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.permission-content { background: #fff; border-radius: 20rpx; width: 600rpx; overflow: hidden; }
.permission-header { padding: 40rpx 30rpx 20rpx; text-align: center; }
.permission-title { font-size: 32rpx; font-weight: 600; color: #333; }
.permission-body { padding: 0 30rpx 40rpx; text-align: center; }
.permission-text { font-size: 28rpx; color: #666; line-height: 1.5; }
.permission-actions { display: flex; border-top: 1rpx solid #eee; }
.permission-btn { flex: 1; text-align: center; padding: 30rpx; font-size: 28rpx; }
.permission-btn.cancel { color: #999; border-right: 1rpx solid #eee; }
.permission-btn.confirm { color: #b8d4ff; font-weight: 500; }
.permission-btn:active { background: #f5f5f5; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(20rpx); } to { opacity: 1; transform: translateY(0); } }
.flight-card, .train-card, .bus-card, .car-rental-card, .entry-card { animation: fadeIn 0.5s ease forwards; }
</style>