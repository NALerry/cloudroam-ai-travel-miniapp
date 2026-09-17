<template>
  <view class="weather-page">
    <!-- 顶部公告轮播 -->
    <view class="announcement-bar" v-if="announcements.length > 0">
      <view class="announcement-icon">
        <uni-icons type="sound" size="16" color="#fff"></uni-icons>
      </view>
      <swiper 
        class="announcement-swiper" 
        vertical 
        autoplay 
        :interval="3000" 
        :duration="500"
        :circular="true"
        :disable-touch="true"
      >
        <swiper-item 
          v-for="(announcement, index) in announcements" 
          :key="index"
          class="announcement-item"
        >
          <text class="announcement-text">{{ announcement.text }}</text>
          <text class="announcement-time">{{ announcement.time }}</text>
        </swiper-item>
      </swiper>
    </view>

    <!-- 顶部搜索栏 -->
    <view 
      class="search-section" 
      :class="{ 'search-hidden': isSearchHidden }"
    >
      <view class="search-bar">
        <uni-icons type="search" size="18" color="#999" class="search-icon"></uni-icons>
        <input 
          class="search-input"
          :placeholder="searchPlaceholder"
          v-model="searchKeyword"
          @focus="onSearchFocus"
          @blur="onSearchBlur"
          @input="onSearchInput"
          @confirm="onSearchConfirm"
          confirm-type="search"
        />
        <uni-icons 
          v-if="searchKeyword" 
          type="clear" 
          size="18" 
          color="#999" 
          class="clear-icon"
          @click="clearSearch"
        ></uni-icons>
      </view>
      
      <!-- 搜索结果下拉列表 -->
      <view class="search-results-dropdown" v-if="showSearchResults">
        <view class="search-history" v-if="searchResults.length === 0 && searchHistory.length > 0">
          <view class="search-header">
            <text class="search-title">搜索历史</text>
            <view class="search-actions">
              <text class="clear-history" @click="clearSearchHistory">清空</text>
            </view>
          </view>
          <scroll-view class="results-list" scroll-y>
            <view 
              class="result-item" 
              v-for="(history, index) in searchHistory" 
              :key="'history-' + index"
              @click="selectSearchHistory(history)"
            >
              <uni-icons type="location" size="16" color="#666"></uni-icons>
              <text class="result-name">{{ history.name }}</text>
              <text class="result-path">{{ history.path }}</text>
            </view>
          </scroll-view>
        </view>
        
        <view class="search-results-content" v-if="searchResults.length > 0">
          <view class="search-header">
            <text class="search-title">搜索结果</text>
          </view>
          <scroll-view class="results-list" scroll-y>
            <view 
              class="result-item" 
              v-for="(result, index) in searchResults" 
              :key="index"
              @click="selectSearchResult(result)"
            >
              <uni-icons type="location" size="16" color="#666"></uni-icons>
              <text class="result-name">{{ result.name }}</text>
              <text class="result-path">{{ result.path }}</text>
            </view>
          </scroll-view>
        </view>
        
        <view class="no-results" v-if="searchResults.length === 0 && searchHistory.length === 0 && !searchLoading">
          <view class="no-results-content">
            <uni-icons type="search" size="32" color="#ccc"></uni-icons>
            <text class="no-results-text">搜索城市天气</text>
            <text class="no-results-tip">支持城市名称、拼音、区号等</text>
          </view>
        </view>

        <view class="search-loading" v-if="searchLoading">
          <view class="search-loading-content">
            <uni-icons type="spinner-cycle" size="24" color="#999" class="loading-icon"></uni-icons>
            <text class="search-loading-text">搜索中...</text>
          </view>
        </view>
      </view>
    </view>

    <swiper 
      class="city-swiper" 
      :current="swiperCurrent"
      @change="onSwiperChange"
      :style="{ flex: 1 }"
    >
      <swiper-item v-for="(city, idx) in cities" :key="city.id">
        <view class="delete-city-btn" v-if="idx !== 0" @click.stop="deleteCity(idx)">
          <uni-icons type="trash" size="20" color="#fff"></uni-icons>
        </view>
        
        <scroll-view 
          class="content-scroll" 
          scroll-y 
          :scroll-top="scrollTop"
          @scroll="onScroll"
          :show-scrollbar="false"
          @touchstart="onTouchStart"
          @touchmove="onTouchMove"
          @touchend="onTouchEnd"
        >
          <view class="loading-section" v-if="city.loading">
            <view class="loading-content">
              <uni-icons type="spinner-cycle" size="48" color="#fff" class="loading-icon"></uni-icons>
              <text class="loading-text">获取天气信息中...</text>
            </view>
          </view>

          <view class="error-section" v-else-if="city.error">
            <view class="error-content">
              <uni-icons type="info" size="48" color="#fff"></uni-icons>
              <text class="error-text">{{ city.errorMessage }}</text>
              <button class="retry-btn" @tap="retryCityWeather(idx)">重新加载</button>
            </view>
          </view>

          <template v-else>
            <view class="current-weather">
              <view class="location-info">
                <view class="city-name">
                  <text class="city">{{ city.currentWeather.city }}</text>
                  <uni-icons type="location" size="16" color="#666"></uni-icons>
                </view>
                <text class="update-time">更新于 {{ city.currentWeather.updateTime }}</text>
              </view>

              <view class="weather-main">
                <view class="temperature-section">
                  <text class="temperature">{{ city.currentWeather.temperature }}°</text>
                  <text class="weather-desc">{{ city.currentWeather.weather }}</text>
                </view>
                <view class="weather-icon">
                  <!-- 实时天气图标：根据当前时间判断昼夜 -->
                  <image :src="getWeatherIcon(city.currentWeather.weather, isCurrentNight())" mode="aspectFit"></image>
                </view>
              </view>

              <view class="weather-details">
                <view class="detail-item">
                  <text class="label">体感温度</text>
                  <text class="value">{{ city.currentWeather.feelsLike }}°</text>
                </view>
                <view class="detail-item">
                  <text class="label">湿度</text>
                  <text class="value">{{ city.currentWeather.humidity }}%</text>
                </view>
                <view class="detail-item">
                  <text class="label">风向</text>
                  <text class="value">{{ city.currentWeather.windDirection }}</text>
                </view>
                <view class="detail-item">
                  <text class="label">风力等级</text>
                  <text class="value">{{ city.currentWeather.windScale }}</text>
                </view>
              </view>
            </view>

            <view class="hourly-forecast" v-if="city.hourlyForecast.length > 0">
              <view class="section-header">
                <text class="section-title">24小时预报</text>
                <text class="section-subtitle">更新于 {{ city.hourlyUpdateTime }}</text>
              </view>
              <scroll-view class="hourly-list" scroll-x>
                <view 
                  class="hourly-item" 
                  v-for="(hour, index) in city.hourlyForecast" 
                  :key="index"
                >
                  <text class="hour-time">{{ formatHourTime(hour.time) }}</text>
                  <!-- 小时预报图标：根据该小时的时间段判断昼夜 -->
                  <image class="hour-icon" :src="getWeatherIcon(hour.weather, isNightByHour(hour.time))" mode="aspectFit"></image>
                  <text class="hour-temp">{{ hour.temperature }}°</text>
                  <text class="hour-humidity" v-if="hour.humidity">💧{{ hour.humidity }}%</text>
                  <text class="hour-precip" v-if="hour.precip">🌧️{{ hour.precip }}%</text>
                </view>
              </scroll-view>
            </view>

            <view class="daily-forecast" v-if="city.dailyForecast.length > 0">
              <view class="section-header">
                <text class="section-title">七日预报</text>
                <text class="forecast-count">共 {{ city.dailyForecast.length }} 天</text>
              </view>
              <view class="daily-list">
                <view 
                  class="daily-item" 
                  v-for="(day, index) in city.dailyForecast" 
                  :key="index"
                  @tap="showDayDetail(day, idx)"
                >
                  <text class="day-name">{{ getDayName(day.date, index) }}</text>
                  <view class="day-weather">
                    <view class="day-weather-item">
                      <!-- 白天图标：总是使用白天版本 -->
                      <image class="day-icon" :src="getWeatherIcon(day.text_day, false)" mode="aspectFit"></image>
                      <text class="weather-text">{{ day.text_day }}</text>
                    </view>
                    <view class="day-weather-item">
                      <!-- 夜间图标：强制使用夜晚版本 -->
                      <image class="day-icon" :src="getWeatherIcon(day.text_night, true)" mode="aspectFit"></image>
                      <text class="weather-text">{{ day.text_night }}</text>
                    </view>
                  </view>
                  <view class="temp-range">
                    <text class="max-temp">{{ day.high }}°</text>
                    <text class="min-temp">{{ day.low }}°</text>
                  </view>
                  <view class="wind-info">
                    <text class="wind-direction">{{ day.wind_direction }}</text>
                    <text class="wind-scale">{{ day.wind_scale }}级</text>
                  </view>
                  <view class="precip-humidity">
                    <text class="precip">💧{{ day.precip }}%</text>
                    <text class="humidity">💨{{ day.humidity }}%</text>
                  </view>
                </view>
              </view>
            </view>

            <view class="weather-modules">
              <view class="module-grid">
                <view class="module-item wind-module" @tap="showWindDetail(city.currentWeather)">
                  <view class="module-header">
                    <image class="module-icon" src="/static/icons/general/wind.png" mode="aspectFit"></image>
                    <text class="module-title">风速</text>
                  </view>
                  <view class="module-content">
                    <text class="wind-speed">{{ city.currentWeather.windSpeed }} km/h</text>
                    <text class="wind-direction">{{ city.currentWeather.windDirection }}</text>
                  </view>
                  <view class="module-footer">
                    <text class="trend">{{ getWindScale(city.currentWeather.windSpeed) }}</text>
                  </view>
                </view>

                <view class="module-item humidity-module" @tap="showHumidityDetail(city.currentWeather)">
                  <view class="module-header">
                    <image class="module-icon" src="/static/icons/general/humidity.png" mode="aspectFit"></image>
                    <text class="module-title">湿度</text>
                  </view>
                  <view class="module-content">
                    <text class="humidity-value">{{ city.currentWeather.humidity }}%</text>
                    <view class="humidity-bar">
                      <view 
                        class="humidity-fill" 
                        :style="{ width: city.currentWeather.humidity + '%' }"
                      ></view>
                    </view>
                  </view>
                  <view class="module-footer">
                    <text class="comfort-level">{{ getComfortLevel(city.currentWeather.humidity) }}</text>
                  </view>
                </view>

                <view class="module-item precip-module" @tap="showPrecipDetail(city.currentWeather)">
                  <view class="module-header">
                    <image class="module-icon" src="/static/icons/general/rain.png" mode="aspectFit"></image>
                    <text class="module-title">降水概率</text>
                  </view>
                  <view class="module-content">
                    <text class="precip-value">{{ city.currentWeather.precip }}%</text>
                    <view class="precip-bar">
                      <view 
                        class="precip-fill" 
                        :style="{ width: city.currentWeather.precip + '%' }"
                      ></view>
                    </view>
                  </view>
                  <view class="module-footer">
                    <text class="precip-level">{{ getPrecipLevel(city.currentWeather.precip) }}</text>
                  </view>
                </view>

                <view class="module-item aqi-module" @tap="showAqiDetail(city.currentWeather)">
                  <view class="module-header">
                    <image class="module-icon" src="/static/icons/general/air.png" mode="aspectFit"></image>
                    <text class="module-title">空气质量</text>
                  </view>
                  <view class="module-content">
                    <text class="aqi-value" :class="getAqiClass(city.currentWeather.aqi)">
                      {{ city.currentWeather.aqiText || '--' }}
                    </text>
                    <text class="aqi-desc" v-if="city.currentWeather.aqiDesc">
                      {{ city.currentWeather.aqiDesc }}
                    </text>
                  </view>
                  <view class="module-footer">
                    <text class="aqi-level">{{ getAqiLevel(city.currentWeather.aqi) }}</text>
                  </view>
                </view>
              </view>
            </view>

            <view class="living-index-section" v-if="city.livingIndexes.length > 0">
              <view class="section-header">
                <text class="section-title">生活指数</text>
              </view>
              <view class="index-grid">
                <view 
                  class="index-item" 
                  v-for="(index, idx) in city.livingIndexes" 
                  :key="idx"
                  @tap="showIndexDetail(index)"
                >
                  <view class="index-icon-wrapper">
                    <image class="index-icon" :src="getLivingIndexIcon(index.name)" mode="aspectFit"></image>
                  </view>
                  <text class="index-name">{{ index.name }}</text>
                  <text class="index-value">{{ index.brief }}</text>
                  <text class="index-desc">{{ index.details }}</text>
                </view>
              </view>
            </view>
            
            <view class="bottom-padding"></view>
          </template>
        </scroll-view>
      </swiper-item>
    </swiper>
  </view>
</template>

<script>
// 心知天气API配置
const WEATHER_API_CONFIG = {
  baseURL: 'https://api.seniverse.com/v3',
  apiKey: '',
  endpoints: {
    now: '/weather/now.json',
    daily: '/weather/daily.json',
    location: '/location/search.json'
  }
};

// 备用IP定位服务（免费，无需key）
const BACKUP_IP_API = 'http://ip-api.com/json/?fields=status,country,regionName,city,lat,lon,query';

export default {
  data() {
    return {
      isSearchHidden: false,
      scrollTop: 0,
      lastScrollTop: 0,
      isDragging: false,
      startY: 0,
      searchPlaceholder: '搜索城市天气',
      searchKeyword: '',
      searchResults: [],
      searchHistory: [],
      searchLoading: false,
      showSearchResults: false,
      
      cities: [],
      swiperCurrent: 0,
      
      announcements: [],
      apiErrorCount: 0,
      maxApiRetries: 3,
    }
  },
  onLoad() {
    this.loadSearchHistory();
    this.initLocationAndCity();
  },
  onPullDownRefresh() {
    this.refreshCurrentCity();
  },
  methods: {
    // ========== 优先使用GPS/网络定位（高精度），失败则降级IP定位 ==========
    async initLocationAndCity() {
      uni.showLoading({ title: '定位中...', mask: true });
      try {
        // 第一步：尝试获取精确经纬度（需要用户授权）
        let locationInfo = await this.getPreciseLocation();
        if (locationInfo && locationInfo.latitude && locationInfo.longitude) {
          console.log('📍 GPS定位成功，经纬度:', locationInfo.latitude, locationInfo.longitude);
          // 心知天气支持 location=纬度:经度 格式
          const coords = `${locationInfo.latitude}:${locationInfo.longitude}`;
          const weatherData = await this.fetchWeatherDataForLocation(coords);
          const newCity = this.createCityObject(weatherData);
          // 如果心知返回的城市名与GPS解析的城市名不一致，可以用GPS解析的城市名覆盖（可选）
          if (locationInfo.cityName && locationInfo.cityName !== newCity.currentWeather.city) {
            console.log(`城市名修正: ${newCity.currentWeather.city} -> ${locationInfo.cityName}`);
            newCity.currentWeather.city = locationInfo.cityName;
            newCity.name = locationInfo.cityName;
          }
          this.cities = [newCity];
          this.swiperCurrent = 0;
        } else {
          throw new Error('GPS定位未获取到有效坐标');
        }
      } catch (gpsError) {
        console.warn('GPS定位失败，回退到IP定位:', gpsError);
        // 降级：使用IP定位（主备双保险）
        try {
          const ipCityInfo = await this.getCityByIPWithFallback();
          if (ipCityInfo && ipCityInfo.id) {
            const weatherData = await this.fetchWeatherDataForLocation(ipCityInfo.id);
            const newCity = this.createCityObject(weatherData);
            newCity.name = ipCityInfo.name;
            newCity.currentWeather.city = ipCityInfo.name;
            this.cities = [newCity];
            this.swiperCurrent = 0;
          } else {
            throw new Error('IP定位未返回有效城市');
          }
        } catch (ipError) {
          console.error('IP定位也失败，使用默认北京:', ipError);
          const defaultData = await this.fetchWeatherDataForLocation('北京');
          const defaultCity = this.createCityObject(defaultData);
          this.cities = [defaultCity];
          this.swiperCurrent = 0;
          uni.showToast({ title: '定位失败，已显示默认城市', icon: 'none', duration: 2000 });
        }
      } finally {
        uni.hideLoading();
      }
    },
    
    // 获取精确地理位置（GPS/网络/WiFi）
    getPreciseLocation() {
      return new Promise((resolve, reject) => {
        uni.getLocation({
          type: 'gcj02', // 返回国测局坐标
          success: (res) => {
            resolve({
              latitude: res.latitude,
              longitude: res.longitude,
              accuracy: res.accuracy
            });
          },
          fail: (err) => {
            console.error('getLocation失败:', err);
            reject(err);
          }
        });
      });
    },
    
    // 增强IP定位：先用心知天气，失败则用备用ip-api.com
    async getCityByIPWithFallback() {
      try {
        const data = await this.makeWeatherAPIRequest(WEATHER_API_CONFIG.endpoints.location, {
          q: 'ip',
          limit: 1,
          language: 'zh-Hans'
        });
        if (data.results && data.results.length > 0) {
          const location = data.results[0];
          return {
            id: location.id,
            name: location.name,
            path: location.path
          };
        } else {
          throw new Error('心知IP定位返回空');
        }
      } catch (primaryError) {
        console.warn('主IP定位失败，尝试备用定位:', primaryError);
        try {
          const backupResult = await this.getLocationByIpApi();
          if (backupResult && backupResult.city) {
            const searchData = await this.makeWeatherAPIRequest(WEATHER_API_CONFIG.endpoints.location, {
              q: backupResult.city,
              limit: 1,
              language: 'zh-Hans'
            });
            if (searchData.results && searchData.results.length > 0) {
              const location = searchData.results[0];
              return {
                id: location.id,
                name: location.name,
                path: location.path
              };
            } else {
              throw new Error('备用定位城市无法转换为有效ID');
            }
          } else {
            throw new Error('备用定位无城市信息');
          }
        } catch (backupError) {
          console.error('备用IP定位也失败:', backupError);
          throw new Error('所有IP定位方式均失败');
        }
      }
    },
    
    getLocationByIpApi() {
      return new Promise((resolve, reject) => {
        uni.request({
          url: BACKUP_IP_API,
          method: 'GET',
          timeout: 8000,
          success: (res) => {
            if (res.statusCode === 200 && res.data && res.data.status === 'success') {
              resolve({
                city: res.data.city,
                region: res.data.regionName,
                country: res.data.country,
                lat: res.data.lat,
                lon: res.data.lon
              });
            } else {
              reject(new Error('ip-api返回失败: ' + (res.data?.message || '未知错误')));
            }
          },
          fail: (err) => {
            reject(new Error('请求ip-api失败: ' + err.errMsg));
          }
        });
      });
    },
    
    // 获取实时天气（心知 now 接口）
    async fetchCurrentWeather(location) {
      try {
        const data = await this.makeWeatherAPIRequest(WEATHER_API_CONFIG.endpoints.now, {
          location: location,
          language: 'zh-Hans',
          unit: 'c'
        });
        if (data.results && data.results.length > 0) {
          const result = data.results[0];
          const now = result.now;
          const locationInfo = result.location;
          return {
            location: locationInfo,
            temperature: Math.round(now.temperature),
            weather: now.text,
            feelsLike: now.feels_like ? Math.round(now.feels_like) : Math.round(now.temperature),
            humidity: now.humidity !== undefined ? parseInt(now.humidity) : null,
            windSpeed: now.wind_speed ? parseFloat(now.wind_speed) : null,
            windDirection: now.wind_direction || null,
            updateTime: this.formatTime(new Date())
          };
        } else {
          throw new Error('实时天气数据格式错误');
        }
      } catch (error) {
        console.error('❌ 获取实时天气失败:', error);
        return null; // 返回null，让上层降级处理
      }
    },
    
    // 获取7天天气预报（心知 daily 接口）
    async fetchDailyWeather(location) {
      try {
        const data = await this.makeWeatherAPIRequest(WEATHER_API_CONFIG.endpoints.daily, {
          location: location,
          start: 0,
          days: 7,
          language: 'zh-Hans',
          unit: 'c'
        });
        if (data.results && data.results.length > 0) {
          const result = data.results[0];
          return {
            location: result.location,
            daily: result.daily,
            last_update: result.last_update
          };
        } else {
          throw new Error('每日预报数据格式错误');
        }
      } catch (error) {
        console.error('❌ 获取每日预报失败:', error);
        throw error;
      }
    },
    
    // 获取完整天气数据（实时 + 每日预报）
    async fetchWeatherDataForLocation(locationParam) {
      try {
        console.log('🌤️ 获取天气数据，位置参数：', locationParam);
        
        // 并行请求实时天气和每日预报
        const [currentWeatherData, dailyWeatherData] = await Promise.all([
          this.fetchCurrentWeather(locationParam),
          this.fetchDailyWeather(locationParam)
        ]);
        
        const locationInfo = dailyWeatherData.location;
        const dailyList = dailyWeatherData.daily;
        const todayDaily = dailyList[0];
        
        // 处理实时数据（如果实时接口成功则使用，否则基于每日预报生成模拟实时数据）
        let currentWeather = {};
        if (currentWeatherData) {
          // 实时数据存在，但某些字段可能为null，需要从每日预报中补充
          currentWeather = {
            city: locationInfo.name,
            temperature: currentWeatherData.temperature,
            weather: currentWeatherData.weather,
            feelsLike: currentWeatherData.feelsLike,
            humidity: (currentWeatherData.humidity !== null && currentWeatherData.humidity !== undefined) 
                      ? currentWeatherData.humidity 
                      : (todayDaily.humidity || 65),
            windSpeed: (currentWeatherData.windSpeed !== null && currentWeatherData.windSpeed !== undefined)
                      ? currentWeatherData.windSpeed
                      : (todayDaily.wind_speed || 10),
            windDirection: currentWeatherData.windDirection || todayDaily.wind_direction || '东南风',
            windScale: '', // 稍后根据风速计算
            precip: todayDaily.precip || 0,
            aqi: 0,
            aqiText: '--',
            aqiDesc: '',
            updateTime: currentWeatherData.updateTime
          };
        } else {
          // 完全降级：使用每日预报第一天的数据估算当前天气
          const avgTemp = Math.round((parseInt(todayDaily.high) + parseInt(todayDaily.low)) / 2);
          currentWeather = {
            city: locationInfo.name,
            temperature: avgTemp,
            weather: todayDaily.text_day || '未知',
            feelsLike: avgTemp,
            humidity: todayDaily.humidity || 65,
            windSpeed: todayDaily.wind_speed || 10,
            windDirection: todayDaily.wind_direction || '东南风',
            windScale: '',
            precip: todayDaily.precip || 0,
            aqi: 0,
            aqiText: '--',
            aqiDesc: '',
            updateTime: this.formatTime(new Date())
          };
        }
        
        // 计算风力等级（基于风速）
        currentWeather.windScale = this.getWindScale(currentWeather.windSpeed);
        
        // 处理每日预报（最多7天）
        let dailyForecast = dailyList.slice(0, 7);
        if (dailyForecast.length < 7) {
          dailyForecast = this.generateFullWeekForecast(dailyForecast);
        }
        
        // 生成空气质量（心知免费版无AQI，沿用模拟，但会基于城市名）
        this.generateAqiForCity(currentWeather, currentWeather.city);
        
        // 生成小时预报（基于实时天气数据模拟）
        const hourlyForecast = this.generateHourlyForecast(currentWeather);
        const hourlyUpdateTime = this.formatTime(new Date());
        
        // 生活指数（模拟）
        const livingIndexes = this.generateLivingIndexes();
        
        return {
          locationId: locationInfo.id,
          currentWeather,
          dailyForecast,
          hourlyForecast,
          hourlyUpdateTime,
          livingIndexes,
          lastUpdate: new Date().toISOString()
        };
      } catch (error) {
        console.error('❌ 获取天气数据失败：', error);
        throw error;
      }
    },
    
    getMockDailyWeather(locationName) {
      const cityName = typeof locationName === 'string' && locationName !== 'ip' ? locationName : '北京';
      const mockData = this.getMockWeatherByCity(cityName);
      const today = new Date();
      const daily = [];
      for (let i = 0; i < 7; i++) {
        const date = new Date(today);
        date.setDate(today.getDate() + i);
        const dateStr = date.toISOString().split('T')[0];
        let high = mockData.temperature + Math.floor(Math.random() * 6) - 2;
        let low = high - 5 - Math.floor(Math.random() * 4);
        let precip = mockData.precip + Math.floor(Math.random() * 20);
        let humidity = mockData.humidity + Math.floor(Math.random() * 15) - 5;
        let text_day = mockData.weather;
        let text_night = mockData.weather;
        if (precip > 30) text_day = '小雨';
        if (precip > 60) text_day = '中雨';
        
        daily.push({
          date: dateStr,
          text_day: text_day,
          text_night: text_night,
          high: high,
          low: low,
          wind_direction: mockData.windDirection,
          wind_scale: mockData.windScale,
          precip: precip,
          humidity: humidity,
          wind_speed: mockData.windSpeed
        });
      }
      return {
        location: { id: `mock_${cityName}`, name: cityName },
        daily: daily,
        last_update: new Date().toISOString()
      };
    },
    
    getMockWeatherByCity(cityName) {
      const mockMap = {
        '北京': { temperature: 25, weather: '晴', humidity: 65, windSpeed: 12, windDirection: '东南风', windScale: '3-4级', precip: 10 },
        '上海': { temperature: 27, weather: '多云', humidity: 70, windSpeed: 10, windDirection: '东风', windScale: '2-3级', precip: 20 },
        '广州': { temperature: 30, weather: '晴', humidity: 75, windSpeed: 8, windDirection: '南风', windScale: '2级', precip: 5 },
        '深圳': { temperature: 31, weather: '多云', humidity: 72, windSpeed: 9, windDirection: '东南风', windScale: '2-3级', precip: 15 },
        '杭州': { temperature: 26, weather: '小雨', humidity: 80, windSpeed: 7, windDirection: '东北风', windScale: '1-2级', precip: 60 },
        '南京': { temperature: 24, weather: '阴', humidity: 68, windSpeed: 11, windDirection: '北风', windScale: '3级', precip: 30 },
        '成都': { temperature: 23, weather: '多云', humidity: 78, windSpeed: 6, windDirection: '西南风', windScale: '1级', precip: 25 },
        '武汉': { temperature: 28, weather: '晴', humidity: 65, windSpeed: 10, windDirection: '东风', windScale: '2-3级', precip: 10 },
        '西安': { temperature: 22, weather: '晴', humidity: 60, windSpeed: 13, windDirection: '西北风', windScale: '3-4级', precip: 5 },
        '重庆': { temperature: 29, weather: '多云', humidity: 75, windSpeed: 8, windDirection: '南风', windScale: '2级', precip: 20 }
      };
      return mockMap[cityName] || mockMap['北京'];
    },
    
    generateHourlyForecast(currentWeather) {
      const now = new Date();
      const currentHour = now.getHours();
      const forecasts = [];
      const currentTemp = currentWeather.temperature;
      const currentWeatherDesc = currentWeather.weather;
      const baseHumidity = currentWeather.humidity;
      
      for (let i = 0; i < 24; i++) {
        const hour = (currentHour + i) % 24;
        let weather = currentWeatherDesc;
        let temp = currentTemp;
        let humidity = baseHumidity;
        let precip = Math.floor(Math.random() * 30);
        
        if (hour < 6 || hour > 20) {
          temp = currentTemp - 5 - Math.floor(Math.random() * 3);
          if (currentWeatherDesc === '晴') {
            weather = Math.random() > 0.7 ? '多云' : '晴';
          }
        } else if (hour > 10 && hour < 16) {
          temp = currentTemp + 2 + Math.floor(Math.random() * 3);
        } else {
          temp = currentTemp - 1 + Math.floor(Math.random() * 2);
        }
        
        if (precip > 20) {
          if (precip < 40) {
            weather = '小雨';
          } else {
            weather = '中雨';
          }
        }
        
        if (weather.includes('雨')) {
          humidity = 80 + Math.floor(Math.random() * 15);
          precip = 30 + Math.floor(Math.random() * 50);
        } else {
          humidity = baseHumidity + Math.floor(Math.random() * 15) - 5;
          humidity = Math.min(95, Math.max(30, humidity));
        }
        
        forecasts.push({
          time: `${hour}`,
          weather: weather,
          temperature: Math.round(temp),
          humidity: humidity,
          precip: precip
        });
      }
      return forecasts;
    },
    
    generateAqiForCity(currentWeather, cityName) {
      const cityAqiMap = {
        '北京': { aqi: 85, text: '良', desc: '空气质量可接受' },
        '上海': { aqi: 65, text: '良', desc: '空气质量可接受' },
        '广州': { aqi: 75, text: '良', desc: '空气质量可接受' },
        '深圳': { aqi: 60, text: '良', desc: '空气质量可接受' },
        '杭州': { aqi: 80, text: '良', desc: '空气质量可接受' },
        '南京': { aqi: 90, text: '良', desc: '空气质量可接受' },
        '成都': { aqi: 95, text: '轻度污染', desc: '敏感人群应减少户外活动' },
        '武汉': { aqi: 70, text: '良', desc: '空气质量可接受' },
        '西安': { aqi: 110, text: '轻度污染', desc: '敏感人群应减少户外活动' },
        '重庆': { aqi: 105, text: '轻度污染', desc: '敏感人群应减少户外活动' }
      };
      const aqiData = cityAqiMap[cityName] || { aqi: 75, text: '良', desc: '空气质量可接受' };
      currentWeather.aqi = aqiData.aqi;
      currentWeather.aqiText = aqiData.text;
      currentWeather.aqiDesc = aqiData.desc;
    },
    
    generateLivingIndexes() {
      return [
        { name: '洗车指数', brief: '适宜', details: '未来两天无雨天气较好' },
        { name: '穿衣指数', brief: '舒适', details: '建议穿长袖衬衫单裤等' },
        { name: '感冒指数', brief: '少发', details: '无明显降温，感冒机率较低' },
        { name: '运动指数', brief: '适宜', details: '天气较好，尽情感受运动的快乐' },
        { name: '旅游指数', brief: '适宜', details: '天气较好，适合外出旅游' },
        { name: '紫外线指数', brief: '中等', details: '涂擦SPF15以上护肤品' }
      ];
    },
    
    generateFullWeekForecast(apiData) {
      const fullWeekData = [...apiData];
      const today = new Date();
      const lastApiDay = apiData.length > 0 ? apiData[apiData.length - 1] : null;
      
      for (let i = apiData.length; i < 7; i++) {
        const date = new Date(today);
        date.setDate(today.getDate() + i);
        const dateStr = date.toISOString().split('T')[0];
        
        let high, low, text_day, text_night, precip, humidity;
        let wind_direction, wind_scale;
        
        if (lastApiDay) {
          high = parseInt(lastApiDay.high) + Math.floor(Math.random() * 3) - 1;
          low = parseInt(lastApiDay.low) + Math.floor(Math.random() * 3) - 1;
          
          const weatherTypes = ['晴', '多云', '阴', '小雨', '中雨'];
          const currentTypeIndex = weatherTypes.indexOf(lastApiDay.text_day);
          let newTypeIndex = currentTypeIndex + Math.floor(Math.random() * 3) - 1;
          newTypeIndex = Math.max(0, Math.min(weatherTypes.length - 1, newTypeIndex));
          text_day = weatherTypes[newTypeIndex];
          text_night = weatherTypes[newTypeIndex];
          
          if (text_day.includes('雨')) {
            precip = 30 + Math.floor(Math.random() * 50);
            humidity = 70 + Math.floor(Math.random() * 20);
          } else {
            precip = Math.floor(Math.random() * 30);
            humidity = 50 + Math.floor(Math.random() * 30);
          }
          
          wind_direction = lastApiDay.wind_direction;
          wind_scale = lastApiDay.wind_scale;
        } else {
          high = 20 + Math.floor(Math.random() * 15);
          low = high - 5 - Math.floor(Math.random() * 5);
          text_day = ['晴', '多云', '阴', '小雨'][Math.floor(Math.random() * 4)];
          text_night = text_day;
          precip = Math.floor(Math.random() * 50);
          humidity = 50 + Math.floor(Math.random() * 40);
          wind_direction = ['东风', '南风', '西风', '北风'][Math.floor(Math.random() * 4)];
          wind_scale = Math.floor(Math.random() * 5) + 1;
        }
        
        fullWeekData.push({
          date: dateStr,
          text_day: text_day,
          text_night: text_night,
          high: high,
          low: low,
          wind_direction: wind_direction,
          wind_scale: wind_scale,
          precip: precip,
          humidity: humidity
        });
      }
      return fullWeekData;
    },
    
    createCityObject(weatherData) {
      return {
        id: weatherData.locationId || Date.now().toString(),
        name: weatherData.currentWeather.city,
        loading: false,
        error: false,
        errorMessage: '',
        currentWeather: weatherData.currentWeather,
        dailyForecast: weatherData.dailyForecast,
        hourlyForecast: weatherData.hourlyForecast,
        hourlyUpdateTime: weatherData.hourlyUpdateTime,
        livingIndexes: weatherData.livingIndexes,
        lastUpdate: weatherData.lastUpdate
      };
    },
    
    async refreshCurrentCity() {
      if (this.cities.length === 0) return;
      const idx = this.swiperCurrent;
      const city = this.cities[idx];
      if (!city) return;
      
      city.loading = true;
      city.error = false;
      this.$forceUpdate();
      
      try {
        const locationId = city.id;
        const newData = await this.fetchWeatherDataForLocation(locationId);
        const updatedCity = this.createCityObject(newData);
        Object.assign(city, updatedCity);
        city.loading = false;
        uni.showToast({ title: '刷新成功', icon: 'success' });
      } catch (err) {
        city.error = true;
        city.errorMessage = err.message || '加载失败';
        city.loading = false;
        uni.showToast({ title: '刷新失败', icon: 'none' });
      } finally {
        this.$forceUpdate();
        uni.stopPullDownRefresh();
      }
    },
    
    async retryCityWeather(idx) {
      const city = this.cities[idx];
      city.loading = true;
      city.error = false;
      this.$forceUpdate();
      
      try {
        const locationId = city.id;
        const newData = await this.fetchWeatherDataForLocation(locationId);
        const updatedCity = this.createCityObject(newData);
        Object.assign(city, updatedCity);
        city.loading = false;
      } catch (err) {
        city.error = true;
        city.errorMessage = err.message || '加载失败';
        city.loading = false;
      } finally {
        this.$forceUpdate();
      }
    },
    
    async makeWeatherAPIRequest(endpoint, params = {}, timeout = 10000) {
      const queryParams = {
        key: WEATHER_API_CONFIG.apiKey,
        language: 'zh-Hans',
        unit: 'c',
        ...params
      };
      
      if (queryParams.location && typeof queryParams.location === 'object') {
        queryParams.location = queryParams.location.name || queryParams.location.id;
      }
      
      const url = `${WEATHER_API_CONFIG.baseURL}${endpoint}`;
      
      return new Promise((resolve, reject) => {
        uni.request({
          url: url,
          method: 'GET',
          data: queryParams,
          timeout: timeout,
          success: (res) => {
            if (res.statusCode === 200) {
              if (res.data.status && res.data.status !== 'OK') {
                reject(new Error(res.data.status || 'API返回错误'));
                return;
              }
              if (!res.data.results || res.data.results.length === 0) {
                reject(new Error('API返回空数据'));
                return;
              }
              resolve(res.data);
            } else if (res.statusCode === 401) {
              reject(new Error('API密钥无效或已过期'));
            } else if (res.statusCode === 429) {
              reject(new Error('API调用频率超限'));
            } else {
              reject(new Error(`HTTP ${res.statusCode}: ${res.errMsg}`));
            }
          },
          fail: (err) => {
            let errorMsg = '网络请求失败';
            if (err.errMsg.includes('timeout')) {
              errorMsg = '请求超时，请检查网络连接';
            } else if (err.errMsg.includes('fail')) {
              errorMsg = '网络连接失败，请检查网络设置';
            }
            reject(new Error(errorMsg));
          }
        });
      });
    },
    
    async searchCity(keyword) {
      if (!keyword.trim()) {
        this.searchResults = [];
        this.showSearchResults = true;
        return;
      }
      
      this.searchLoading = true;
      this.searchResults = [];
      
      try {
        const data = await this.makeWeatherAPIRequest(WEATHER_API_CONFIG.endpoints.location, {
          q: keyword.trim(),
          limit: 10,
          language: 'zh-Hans'
        });
        
        if (data.results && data.results.length > 0) {
          this.searchResults = data.results.map(item => ({
            id: item.id,
            name: item.name,
            path: item.path,
            country: item.country
          }));
        } else {
          this.searchResults = [];
        }
        this.showSearchResults = true;
        
        if (this.searchResults.length === 0) {
          uni.showToast({ title: '未找到相关城市', icon: 'none', duration: 1500 });
        }
      } catch (error) {
        console.error('搜索城市失败:', error);
        uni.showToast({ title: '搜索失败: ' + error.message, icon: 'none', duration: 2000 });
      } finally {
        this.searchLoading = false;
      }
    },
    
    async selectSearchResult(result) {
      const existIndex = this.cities.findIndex(c => c.id === result.id || c.name === result.name);
      if (existIndex !== -1) {
        this.swiperCurrent = existIndex;
        this.closeSearchResults();
        this.searchKeyword = '';
        uni.showToast({ title: `切换到${result.name}`, icon: 'success' });
        return;
      }
      
      uni.showLoading({ title: `添加${result.name}...`, mask: true });
      try {
        const weatherData = await this.fetchWeatherDataForLocation(result.id);
        const newCity = this.createCityObject(weatherData);
        newCity.id = result.id;
        newCity.name = result.name;
        this.cities.push(newCity);
        this.swiperCurrent = this.cities.length - 1;
        this.addToSearchHistory(result);
        uni.showToast({ title: `已添加${result.name}`, icon: 'success' });
      } catch (err) {
        console.error('添加城市失败:', err);
        uni.showToast({ title: '添加失败', icon: 'none' });
      } finally {
        uni.hideLoading();
        this.closeSearchResults();
        this.searchKeyword = '';
      }
    },
    
    selectSearchHistory(history) {
      this.selectSearchResult(history);
    },
    
    addToSearchHistory(result) {
      this.searchHistory = this.searchHistory.filter(item => item.id !== result.id);
      this.searchHistory.unshift({
        id: result.id,
        name: result.name,
        path: result.path
      });
      if (this.searchHistory.length > 5) {
        this.searchHistory = this.searchHistory.slice(0, 5);
      }
      this.saveSearchHistory();
    },
    
    loadSearchHistory() {
      try {
        const history = uni.getStorageSync('weatherSearchHistory');
        if (history) {
          this.searchHistory = JSON.parse(history);
        }
      } catch (error) {
        console.error('加载搜索历史失败:', error);
      }
    },
    
    saveSearchHistory() {
      try {
        uni.setStorageSync('weatherSearchHistory', JSON.stringify(this.searchHistory));
      } catch (error) {
        console.error('保存搜索历史失败:', error);
      }
    },
    
    clearSearchHistory() {
      this.searchHistory = [];
      this.saveSearchHistory();
      uni.showToast({ title: '搜索历史已清空', icon: 'success' });
    },
    
    deleteCity(index) {
      if (this.cities.length <= 1) {
        uni.showToast({ title: '至少保留一个城市', icon: 'none' });
        return;
      }
      const cityName = this.cities[index].name;
      uni.showModal({
        title: '删除城市',
        content: `确定要删除「${cityName}」吗？`,
        success: (res) => {
          if (res.confirm) {
            this.cities.splice(index, 1);
            let newIndex = this.swiperCurrent;
            if (index === newIndex) {
              newIndex = Math.min(newIndex, this.cities.length - 1);
            } else if (index < newIndex) {
              newIndex--;
            }
            this.swiperCurrent = newIndex;
            this.$forceUpdate();
            uni.showToast({ title: '已删除', icon: 'success' });
          }
        }
      });
    },
    
    onSwiperChange(e) {
      this.swiperCurrent = e.detail.current;
    },
    
    async loadAnnouncements() {
      try {
        this.announcements = [
          { text: '🌤️ 温馨提示：近期天气变化较大，请及时关注天气预报', time: '今天', type: 'info' },
          { text: '💧 空气干燥，请注意补水保湿', time: '今天', type: 'info' }
        ];
      } catch (error) {
        console.error('加载公告失败:', error);
      }
    },
    
    onSearchInput(e) {
      this.searchKeyword = e.detail.value;
      if (this.searchKeyword.trim()) {
        this.searchCity(this.searchKeyword);
      } else {
        this.searchResults = [];
        this.showSearchResults = true;
      }
    },
    
    onSearchFocus() {
      this.showSearchResults = true;
      if (this.searchKeyword.trim()) {
        this.searchCity(this.searchKeyword);
      }
    },
    
    onSearchBlur() {
      setTimeout(() => {
        this.closeSearchResults();
      }, 200);
    },
    
    onSearchConfirm() {
      if (this.searchKeyword.trim()) {
        this.searchCity(this.searchKeyword.trim());
      }
    },
    
    clearSearch() {
      this.searchKeyword = '';
      this.searchResults = [];
      this.showSearchResults = true;
    },
    
    closeSearchResults() {
      this.showSearchResults = false;
      this.searchLoading = false;
    },
    
    onScroll(e) {
      const scrollTop = e.detail.scrollTop;
      if (scrollTop <= 0 && this.isSearchHidden) {
        this.showSearchBar();
      } else if (scrollTop > 50 && !this.isSearchHidden) {
        this.hideSearchBar();
      }
      this.lastScrollTop = scrollTop;
    },
    
    onTouchStart(e) {
      this.startY = e.touches[0].clientY;
      this.isDragging = true;
    },
    
    onTouchMove(e) {
      if (!this.isSearchHidden) return;
      const currentY = e.touches[0].clientY;
      const diff = currentY - this.startY;
      if (diff > 50) {
        this.showSearchBar();
      }
    },
    
    onTouchEnd() {
      this.isDragging = false;
    },
    
    showSearchBar() {
      this.isSearchHidden = false;
      this.scrollTop = 0;
    },
    
    hideSearchBar() {
      this.isSearchHidden = true;
    },
    
    // ========== 昼夜判断方法 ==========
    // 判断当前是否为夜晚（基于设备时间）
    isCurrentNight() {
      const hour = new Date().getHours();
      return hour >= 18 || hour < 6;
    },
    
    // 根据小时字符串（如 "8"、"20"）判断该小时是否为夜晚
    isNightByHour(hourStr) {
      if (!hourStr && hourStr !== 0) return false;
      const hour = parseInt(hourStr, 10);
      return hour >= 18 || hour < 6;
    },
    
    // 天气图标：根据天气文本和是否为夜晚返回正确的图标路径
    getWeatherIcon(weather, isNight = false) {
      // 白天图标映射（原有全部保留）
      const dayIconMap = {
        '晴': '/static/icons/weather/sunny.png',
        '多云': '/static/icons/weather/cloudy.png',
        '阴': '/static/icons/weather/overcast.png',
        '小雨': '/static/icons/weather/light-rain.png',
        '中雨': '/static/icons/weather/moderate-rain.png',
        '大雨': '/static/icons/weather/heavy-rain.png',
        '暴雨': '/static/icons/weather/heavydownpour.png',
        '雷阵雨': '/static/icons/weather/thunderstorm.png',
        '小雪': '/static/icons/weather/snow.png',
        '中雪': '/static/icons/weather/moderatesnow.png',
        '大雪': '/static/icons/weather/greatsnow.png',
        '暴雪': '/static/icons/weather/snowstorm.png',
        '雾': '/static/icons/weather/fog.png',
        '冰雹': '/static/icons/weather/icerain.png',
        '雨夹雪': '/static/icons/weather/sleet.png',
        '沙尘暴': '/static/icons/weather/sandstorm.png',
        '霾': '/static/icons/weather/fog.png',
      };
      
      // 夜晚图标映射（只有需要区分的天气提供，未提供的会降级使用白天图标）
      const nightIconMap = {
        '晴': '/static/icons/weather/clear-night.png',     // 月亮/晴夜
        '多云': '/static/icons/weather/cloudy-night.png',
        '阴': '/static/icons/weather/overcast-night.png',
        // 雨、雪等夜间与白天差异不大，可选择性添加，不添加则自动fallback到白天图标
      };
      
      let iconPath = '';
      if (isNight && nightIconMap[weather]) {
        iconPath = nightIconMap[weather];
      } else if (dayIconMap[weather]) {
        iconPath = dayIconMap[weather];
      } else {
        // 兜底图标
        iconPath = '/static/icons/weather/cloudy.png';
      }
      
      // 可选：开发环境或真机调试时可打印缺少夜晚图标的警告
      if (isNight && !nightIconMap[weather] && dayIconMap[weather]) {
        console.debug(`夜间图标缺失: ${weather}，使用白天图标替代`);
      }
      return iconPath;
    },
    
    getLivingIndexIcon(type) {
      const iconMap = {
        '洗车指数': '/static/icons/general/car-wash.png',
        '穿衣指数': '/static/icons/general/clothes.png',
        '感冒指数': '/static/icons/general/cold.png',
        '运动指数': '/static/icons/general/sports.png',
        '旅游指数': '/static/icons/general/travel.png',
        '紫外线指数': '/static/icons/general/uv.png'
      };
      return iconMap[type] || '/static/icons/general/uv.png';
    },
    
    getAqiClass(aqi) {
      if (aqi <= 50) return 'excellent';
      if (aqi <= 100) return 'good';
      if (aqi <= 150) return 'light';
      if (aqi <= 200) return 'moderate';
      return 'severe';
    },
    
    getAqiLevel(aqi) {
      if (aqi <= 50) return '优';
      if (aqi <= 100) return '良';
      if (aqi <= 150) return '轻度污染';
      if (aqi <= 200) return '中度污染';
      return '重度污染';
    },
    
    getWindScale(speed) {
      const windSpeed = parseFloat(speed) || 0;
      if (windSpeed < 1) return '无风';
      if (windSpeed < 6) return '微风';
      if (windSpeed < 12) return '和风';
      if (windSpeed < 20) return '清风';
      if (windSpeed < 29) return '强风';
      if (windSpeed < 39) return '疾风';
      return '大风';
    },
    
    getComfortLevel(humidity) {
      const hum = parseInt(humidity) || 0;
      if (hum < 30) return '干燥';
      if (hum < 60) return '舒适';
      if (hum < 80) return '潮湿';
      return '闷热';
    },
    
    getPrecipLevel(precip) {
      const p = parseInt(precip) || 0;
      if (p < 10) return '无雨';
      if (p < 30) return '小雨';
      if (p < 60) return '中雨';
      return '大雨';
    },
    
    formatTime(date) {
      const hours = date.getHours().toString().padStart(2, '0');
      const minutes = date.getMinutes().toString().padStart(2, '0');
      return `${hours}:${minutes}`;
    },
    
    formatHourTime(timeStr) {
      if (!timeStr) return '';
      const hours = parseInt(timeStr);
      const now = new Date();
      const currentHour = now.getHours();
      if (hours === currentHour) return '现在';
      if (hours < 12) return `${hours}时`;
      if (hours === 12) return '12时';
      return `${hours}时`;
    },
    
    getDayName(dateStr, index) {
      if (index === 0) return '今天';
      if (index === 1) return '明天';
      if (index === 2) return '后天';
      const date = new Date(dateStr);
      const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
      return days[date.getDay()];
    },
    
    showWindDetail(weather) {
      uni.showModal({
        title: '风速信息',
        content: `当前风速：${weather.windSpeed} km/h\n风向：${weather.windDirection}\n风力等级：${weather.windScale}\n风力描述：${this.getWindScale(weather.windSpeed)}`,
        showCancel: false
      });
    },
    
    showHumidityDetail(weather) {
      uni.showModal({
        title: '湿度信息',
        content: `当前湿度：${weather.humidity}%\n体感：${this.getComfortLevel(weather.humidity)}`,
        showCancel: false
      });
    },
    
    showPrecipDetail(weather) {
      uni.showModal({
        title: '降水概率',
        content: `降水概率：${weather.precip}%\n降水等级：${this.getPrecipLevel(weather.precip)}`,
        showCancel: false
      });
    },
    
    showAqiDetail(weather) {
      uni.showModal({
        title: '空气质量',
        content: `空气质量：${weather.aqiText}\n等级：${this.getAqiLevel(weather.aqi)}\n${weather.aqiDesc || '无详细描述'}`,
        showCancel: false
      });
    },
    
    showIndexDetail(index) {
      uni.showModal({
        title: index.name,
        content: `等级：${index.brief}\n描述：${index.details}`,
        showCancel: false
      });
    },
    
    showDayDetail(day, cityIdx) {
      uni.showModal({
        title: `${this.getDayName(day.date, this.cities[cityIdx].dailyForecast.indexOf(day))}天气详情`,
        content: `日期：${day.date}\n白天：${day.text_day}\n夜间：${day.text_night}\n温度：${day.low}°C ~ ${day.high}°C\n风向：${day.wind_direction}\n风力：${day.wind_scale}级\n降水概率：${day.precip}%\n湿度：${day.humidity}%`,
        showCancel: false
      });
    }
  }
}
</script>

<style scoped>
.weather-page {
  height: 100vh;
  background: linear-gradient(135deg, #74b9ff 0%, #bcc4e8 100%);
  display: flex;
  flex-direction: column;
  position: relative;
}

.city-swiper {
  flex: 1;
  width: 100%;
}

.delete-city-btn {
  position: absolute;
  top: 20rpx;
  right: 30rpx;
  z-index: 20;
  background: rgba(0, 0, 0, 0.4);
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(8px);
}

.loading-section {
  padding: 100rpx 30rpx;
  display: flex;
  justify-content: center;
  align-items: center;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20rpx;
}

.loading-icon {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  font-size: 28rpx;
  color: #fff;
}

.error-section {
  padding: 100rpx 30rpx;
  display: flex;
  justify-content: center;
  align-items: center;
}

.error-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 30rpx;
}

.error-text {
  font-size: 28rpx;
  color: #fff;
  text-align: center;
}

.retry-btn {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  border: none;
  padding: 20rpx 40rpx;
  border-radius: 50rpx;
  font-size: 28rpx;
}

.retry-btn::after {
  border: none;
}

.announcement-bar {
  background: linear-gradient(90deg, #b8d4ff 0%, #bcc4e8 100%);
  padding: 16rpx 30rpx;
  display: flex;
  align-items: center;
  gap: 20rpx;
  z-index: 10;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.1);
}

.announcement-icon {
  display: flex;
  align-items: center;
}

.announcement-swiper {
  height: 40rpx;
  flex: 1;
}

.announcement-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
}

.announcement-text {
  font-size: 24rpx;
  color: #fff;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.announcement-time {
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.8);
  margin-left: 20rpx;
}

.search-section {
  background: rgba(255, 255, 255, 0.95);
  padding: 20rpx 30rpx;
  transition: transform 0.3s ease, opacity 0.3s ease;
  z-index: 10;
  position: relative;
}

.search-hidden {
  transform: translateY(-100%);
  opacity: 0;
}

.search-bar {
  display: flex;
  align-items: center;
  background: #f5f5f5;
  border-radius: 50rpx;
  padding: 16rpx 24rpx;
  margin-bottom: 16rpx;
  position: relative;
  z-index: 12;
}

.search-icon {
  margin-right: 16rpx;
}

.search-input {
  flex: 1;
  font-size: 28rpx;
  color: #333;
}

.clear-icon {
  margin-left: 16rpx;
}

.search-results-dropdown {
  position: absolute;
  top: 100%;
  left: 30rpx;
  right: 30rpx;
  background: #fff;
  border-radius: 0 0 20rpx 20rpx;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.15);
  z-index: 11;
  max-height: 400rpx;
  overflow: hidden;
}

.search-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
  padding: 20rpx 24rpx 0;
}

.search-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
}

.search-actions {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.clear-history {
  font-size: 24rpx;
  color: #999;
}

.results-list {
  max-height: 300rpx;
  padding: 0 24rpx;
}

.result-item {
  display: flex;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #f5f5f5;
  gap: 16rpx;
}

.result-item:last-child {
  border-bottom: none;
}

.result-name {
  font-size: 28rpx;
  color: #333;
  flex: 1;
}

.result-path {
  font-size: 24rpx;
  color: #666;
}

.no-results {
  padding: 40rpx 30rpx;
  display: flex;
  justify-content: center;
  align-items: center;
}

.no-results-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
}

.no-results-text {
  font-size: 28rpx;
  color: #999;
}

.no-results-tip {
  font-size: 24rpx;
  color: #ccc;
}

.search-loading {
  padding: 30rpx;
  display: flex;
  justify-content: center;
  align-items: center;
}

.search-loading-content {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.search-loading-text {
  font-size: 28rpx;
  color: #999;
}

.content-scroll {
  height: 100%;
  background: linear-gradient(135deg, #74b9ff 0%, #bcc4e8 100%);
}

.current-weather {
  padding: 40rpx 30rpx;
  color: #fff;
}

.location-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40rpx;
}

.city-name {
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.city {
  font-size: 36rpx;
  font-weight: 600;
}

.update-time {
  font-size: 24rpx;
  opacity: 0.8;
}

.weather-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40rpx;
}

.temperature-section {
  display: flex;
  flex-direction: column;
}

.temperature {
  font-size: 96rpx;
  font-weight: 300;
  line-height: 1;
}

.weather-desc {
  font-size: 32rpx;
  opacity: 0.9;
}

.weather-icon {
  width: 120rpx;
  height: 120rpx;
}

.weather-icon image {
  width: 100%;
  height: 100%;
}

.weather-details {
  display: flex;
  flex-wrap: wrap;
  gap: 30rpx;
  justify-content: space-between;
  margin-bottom: 40rpx;
}

.detail-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 120rpx;
}

.detail-item .label {
  font-size: 24rpx;
  opacity: 0.8;
  margin-bottom: 8rpx;
}

.detail-item .value {
  font-size: 28rpx;
  font-weight: 500;
}

.weather-modules {
  padding: 0 30rpx 30rpx;
}

.module-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20rpx;
}

.module-item {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20rpx;
  padding: 30rpx;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.1);
}

.module-header {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.module-icon {
  width: 40rpx;
  height: 40rpx;
  margin-right: 12rpx;
}

.module-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
}

.module-content {
  margin-bottom: 16rpx;
}

.wind-speed {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  display: block;
  margin-bottom: 8rpx;
}

.wind-direction {
  font-size: 24rpx;
  color: #666;
}

.humidity-value {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  display: block;
  margin-bottom: 12rpx;
}

.humidity-bar {
  width: 100%;
  height: 8rpx;
  background: #f0f0f0;
  border-radius: 4rpx;
  overflow: hidden;
}

.humidity-fill {
  height: 100%;
  background: linear-gradient(90deg, #74b9ff, #0984e3);
  border-radius: 4rpx;
  transition: width 0.5s ease;
}

.precip-value {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  display: block;
  margin-bottom: 12rpx;
}

.precip-bar {
  width: 100%;
  height: 8rpx;
  background: #f0f0f0;
  border-radius: 4rpx;
  overflow: hidden;
}

.precip-fill {
  height: 100%;
  background: linear-gradient(90deg, #74b9ff, #0984e3);
  border-radius: 4rpx;
  transition: width 0.5s ease;
}

.aqi-value {
  font-size: 32rpx;
  font-weight: 600;
  display: block;
  margin-bottom: 8rpx;
}

.aqi-value.excellent { color: #00b894; }
.aqi-value.good { color: #00cec9; }
.aqi-value.light { color: #fdcb6e; }
.aqi-value.moderate { color: #e17055; }
.aqi-value.severe { color: #d63031; }

.aqi-desc {
  font-size: 24rpx;
  color: #666;
}

.module-footer {
  border-top: 1rpx solid #f0f0f0;
  padding-top: 12rpx;
}

.trend, .comfort-level, .precip-level, .aqi-level {
  font-size: 22rpx;
  color: #666;
}

.hourly-forecast {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  margin: 0 30rpx 30rpx;
  border-radius: 20rpx;
  padding: 30rpx;
}

.hourly-forecast .section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #fff;
}

.section-subtitle {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.7);
}

.hourly-list {
  white-space: nowrap;
}

.hourly-item {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  padding: 0 20rpx;
  min-width: 80rpx;
}

.hour-time {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 16rpx;
}

.hour-icon {
  width: 50rpx;
  height: 50rpx;
  margin-bottom: 12rpx;
}

.hour-temp {
  font-size: 28rpx;
  color: #fff;
  font-weight: 500;
  margin-bottom: 8rpx;
}

.hour-humidity, .hour-precip {
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 4rpx;
}

.daily-forecast {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  margin: 0 30rpx 30rpx;
  border-radius: 20rpx;
  padding: 30rpx;
}

.daily-forecast .section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
}

.forecast-count {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.7);
}

.daily-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.daily-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 0;
  border-bottom: 1rpx solid rgba(255, 255, 255, 0.2);
}

.daily-item:last-child {
  border-bottom: none;
}

.day-name {
  font-size: 28rpx;
  color: #fff;
  width: 100rpx;
}

.day-weather {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  width: 120rpx;
}

.day-weather-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.day-icon {
  width: 30rpx;
  height: 30rpx;
}

.weather-text {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.8);
}

.temp-range {
  display: flex;
  gap: 20rpx;
  width: 100rpx;
  justify-content: center;
}

.max-temp {
  font-size: 28rpx;
  color: #fff;
  font-weight: 500;
}

.min-temp {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.7);
}

.wind-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100rpx;
  gap: 4rpx;
}

.wind-direction {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.8);
}

.wind-scale {
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.7);
}

.precip-humidity {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100rpx;
  gap: 4rpx;
}

.precip, .humidity {
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.7);
}

.living-index-section {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20rpx;
  padding: 30rpx;
  margin: 0 30rpx 30rpx;
}

.living-index-section .section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
}

.living-index-section .section-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #fff;
}

.living-index-section .index-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 20rpx;
}

.living-index-section .index-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 20rpx;
  border-radius: 16rpx;
  background: rgba(255, 255, 255, 0.2);
}

.living-index-section .index-icon-wrapper {
  width: 60rpx;
  height: 60rpx;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16rpx;
}

.living-index-section .index-icon {
  width: 30rpx;
  height: 30rpx;
}

.living-index-section .index-name {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 8rpx;
}

.living-index-section .index-value {
  font-size: 24rpx;
  color: #fff;
  font-weight: 500;
  margin-bottom: 4rpx;
}

.living-index-section .index-desc {
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.4;
}

.bottom-padding {
  height: 40rpx;
  background: transparent;
}
</style>