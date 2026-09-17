<template>
  <view class="travel-page">
    <!-- 顶部搜索栏 - 左侧天气 + 右侧搜索框 -->
    <view class="search-section">
      <view class="search-container">
        <!-- 天气信息区域：点击左侧区域切换卡片，独立刷新按钮 -->
        <view class="weather-area" v-if="weatherInfo.cityName">
          <view class="weather-main" @tap="toggleWeatherCard">
            <text class="weather-emoji">{{ weatherIcon }}</text>
            <view class="weather-text">
              <text class="city-name">{{ weatherInfo.cityName }}</text>
              <text class="temp-info">{{ weatherInfo.temp }}°C</text>
            </view>
            <text class="weather-desc">{{ weatherInfo.weatherText }}</text>
          </view>
          <!-- 独立刷新按钮，阻止冒泡，避免触发卡片切换 -->
          <view class="weather-refresh" @tap.stop="refreshWeather">
            <text class="refresh-icon">⟳</text>
          </view>
          
          <!-- 天气详情卡片：通过点击天气区域切换显示/隐藏，支持移动端 -->
          <view class="weather-card" v-show="showWeatherCard" @tap.stop>
            <!-- 动态背景效果层，根据天气类型显示不同动画 -->
            <view class="weather-animation-layer" :class="animationClass"></view>
            
            <view class="card-header">
              <view class="header-left">
                <text class="card-city">{{ weatherInfo.cityName }}</text>
                <text class="card-time">实时天气 · {{ weatherInfo.updateTime }}</text>
              </view>
              <view class="header-right">
                <text class="publish-tip">实时发布</text>
              </view>
            </view>
            
            <!-- 主要温度区域 -->
            <view class="card-main-temp">
              <text class="big-temp">{{ weatherInfo.temp }}°</text>
              <view class="temp-range">
                <text class="range-text">白天 {{ dayHighTemp }}° / 夜间 {{ dayLowTemp }}°</text>
                <text class="weather-status">{{ weatherInfo.weatherText }}</text>
              </view>
            </view>
            
            <!-- 详细信息网格 (体感、风力、湿度、AQI等) -->
            <view class="card-details-grid">
              <view class="detail-item">
                <text class="detail-label">体感温度</text>
                <text class="detail-value">{{ weatherInfo.feelsLike }}°</text>
              </view>
              <view class="detail-item">
                <text class="detail-label">风向/风力</text>
                <text class="detail-value">{{ weatherInfo.windDir }} {{ windPowerLevel }}</text>
              </view>
              <view class="detail-item">
                <text class="detail-label">湿度</text>
                <text class="detail-value">{{ weatherInfo.humidity }}%</text>
              </view>
              <view class="detail-item">
                <text class="detail-label">空气质量</text>
                <text class="detail-value">{{ airQualityText }} {{ weatherInfo.aqi || '--' }}</text>
              </view>
              <view class="detail-item">
                <text class="detail-label">紫外线</text>
                <text class="detail-value">{{ uvIndex }}</text>
              </view>
              <view class="detail-item">
                <text class="detail-label">日出/日落</text>
                <text class="detail-value">{{ sunriseTime }}/{{ sunsetTime }}</text>
              </view>
            </view>
            
            <!-- 未来三日预报 -->
            <view class="forecast-3days">
              <view v-for="(day, idx) in forecastDays" :key="idx" class="forecast-item">
                <text class="forecast-week">{{ day.week }}</text>
                <text class="forecast-emoji">{{ day.emoji }}</text>
                <text class="forecast-temp">{{ day.lowTemp }}~{{ day.highTemp }}°</text>
              </view>
            </view>
            
            <!-- 小时天气预报 + 折线图区域 -->
            <view class="hourly-section">
              <view class="hourly-title">小时气温趋势</view>
              <canvas 
                canvas-id="tempTrendCanvas" 
                id="tempTrendCanvas"
                class="trend-canvas"
                :width="canvasWidth"
                :height="160"
                :style="{ width: canvasWidth + 'px', height: '160px' }"
              ></canvas>
              <scroll-view class="hourly-scroll" scroll-x :show-scrollbar="false">
                <view class="hourly-list">
                  <view v-for="(hour, idx) in hourlyForecast" :key="idx" class="hour-item">
                    <text class="hour-time">{{ hour.timeStr }}</text>
                    <text class="hour-temp">{{ hour.temp }}°</text>
                    <text class="hour-weather">{{ hour.weatherEmoji }}</text>
                  </view>
                </view>
              </scroll-view>
            </view>
          </view>
        </view>
        
        <!-- 加载状态或错误占位 -->
        <view class="weather-area loading-area" v-else-if="weatherLoading">
          <text class="loading-text">定位天气中...</text>
        </view>
        <view class="weather-area error-area" v-else @tap="fetchWeather">
          <text class="error-text">点此获取天气</text>
        </view>

        <!-- 搜索栏 -->
        <search-bar 
          :placeholder="searchPlaceholder"
          :auto-focus="false"
          @search="onSearch"
          @focus="onSearchFocus"
          class="search-bar-flex"
        >
          <image slot="left" src="/static/icons/general/search1.png" class="search-icon"></image>
        </search-bar>
      </view>
    </view>

    <!-- 五大功能按钮 -->
    <view class="function-buttons">
      <scroll-view class="buttons-scroll" scroll-x>
        <view 
          class="button-item" 
          v-for="item in functionButtons" 
          :key="item.id"
          @tap="onFunctionButtonTap(item)"
        >
          <view class="button-icon">
            <image class="icon-image" :src="item.icon" mode="aspectFit"></image>
          </view>
          <text class="button-text">{{ item.name }}</text>
        </view>
      </scroll-view>
    </view>

    <!-- Banner轮播图 -->
    <view class="banner-section">
      <swiper 
        class="banner-swiper" 
        indicator-dots 
        autoplay 
        circular 
        interval="3000"
        indicator-active-color="#b8d4ff"
      >
        <swiper-item 
          v-for="(banner, index) in banners" 
          :key="index"
          @tap="onBannerTap(banner)"
        >
          <image class="banner-image" :src="banner.image" mode="aspectFill"></image>
          <view class="banner-mask">
            <text class="banner-title">{{ banner.title }}</text>
            <text class="banner-desc" v-if="banner.desc">{{ banner.desc }}</text>
          </view>
        </swiper-item>
      </swiper>
    </view>

    <!-- AI助手入口 -->
    <view class="ai-assistant-section" @tap="navigateToAIChat">
      <view class="ai-assistant-card">
        <view class="ai-avatar">
          <image class="avatar-image" src="/static/avatars/Dog1.jpg" mode="aspectFit"></image>
          <view class="ai-status"></view>
        </view>
        <view class="ai-content">
          <view class="ai-header">
            <text class="ai-title">AI Dog</text>
            <view class="ai-tag">Always Online</view>
          </view>
          <text class="ai-desc">随时解答您的旅行问题，规划最佳行程</text>
        </view>
        <view class="ai-arrow">
          <text class="arrow-icon">›</text>
        </view>
      </view>
    </view>

    <!-- 功能选择模块 -->
    <view class="function-modules">
      <scroll-view class="modules-scroll" scroll-y>
        <!-- 出行模块 -->
        <view class="module-section">
          <view class="module-header">
            <text class="module-title">出行</text>
            <text class="module-more" @tap="navigateToModule('transport')">更多+</text>
          </view>
          <view class="module-content">
            <scroll-view class="sub-modules-scroll" scroll-x>
              <view 
                class="sub-module" 
                v-for="item in transportModules" 
                :key="item.id"
                @tap="navigateToSubModule('transport', item)"
              >
                <view class="sub-icon">
                  <image :src="item.icon" mode="aspectFit"></image>
                </view>
                <text class="sub-text">{{ item.name }}</text>
              </view>
            </scroll-view>
          </view>
        </view>

        <!-- 住宿模块 -->
        <view class="module-section">
          <view class="module-header">
            <text class="module-title">住宿</text>
            <text class="module-more" @tap="navigateToModule('accommodation')">更多+</text>
          </view>
          <view class="module-content">
            <scroll-view class="sub-modules-scroll" scroll-x>
              <view 
                class="sub-module" 
                v-for="item in accommodationModules" 
                :key="item.id"
                @tap="navigateToSubModule('accommodation', item)"
              >
                <view class="sub-icon">
                  <image :src="item.icon" mode="aspectFit"></image>
                </view>
                <text class="sub-text">{{ item.name }}</text>
              </view>
            </scroll-view>
          </view>
        </view>

        <!-- 美食模块 -->
        <view class="module-section">
          <view class="module-header">
            <text class="module-title">美食</text>
            <text class="module-more" @tap="navigateToModule('food')">更多+</text>
          </view>
          <view class="module-content">
            <scroll-view class="sub-modules-scroll" scroll-x>
              <view 
                class="sub-module" 
                v-for="item in foodModules" 
                :key="item.id"
                @tap="navigateToSubModule('food', item)"
              >
                <view class="sub-icon">
                  <image :src="item.icon" mode="aspectFit"></image>
                </view>
                <text class="sub-text">{{ item.name }}</text>
              </view>
            </scroll-view>
          </view>
        </view>

        <!-- 习俗模块 -->
        <view class="module-section">
          <view class="module-header">
            <text class="module-title">习俗</text>
            <text class="module-more" @tap="navigateToModule('custom')">更多+</text>
          </view>
          <view class="module-content">
            <scroll-view class="sub-modules-scroll" scroll-x>
              <view 
                class="sub-module" 
                v-for="item in customModules" 
                :key="item.id"
                @tap="navigateToSubModule('custom', item)"
              >
                <view class="sub-icon">
                  <image :src="item.icon" mode="aspectFit"></image>
                </view>
                <text class="sub-text">{{ item.name }}</text>
              </view>
            </scroll-view>
          </view>
        </view>

        <!-- 购物模块 -->
        <view class="module-section">
          <view class="module-header">
            <text class="module-title">购物</text>
            <text class="module-more" @tap="navigateToModule('shopping')">更多+</text>
          </view>
          <view class="module-content">
            <scroll-view class="sub-modules-scroll" scroll-x>
              <view 
                class="sub-module" 
                v-for="item in shoppingModules" 
                :key="item.id"
                @tap="navigateToSubModule('shopping', item)"
              >
                <view class="sub-icon">
                  <image :src="item.icon" mode="aspectFit"></image>
                </view>
                <text class="sub-text">{{ item.name }}</text>
              </view>
            </scroll-view>
          </view>
        </view>
      </scroll-view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      showWeatherCard: false,      // 控制天气详情卡片显示
      searchPlaceholder: '搜索目的地、攻略或景点',
      weatherInfo: {
        cityName: '',
        temp: '--',
        weatherText: '获取中',
        weatherCode: '',
        humidity: '--',
        windSpeed: '--',
        windDir: '--',
        feelsLike: '--',
        updateTime: '',
        aqi: '--'
      },
      weatherLoading: true,
      weatherIcon: '🌍',
      dayHighTemp: '--',
      dayLowTemp: '--',
      windPowerLevel: '--级',
      airQualityText: '优',
      uvIndex: '中等',
      sunriseTime: '06:00',
      sunsetTime: '18:00',
      lunarInfo: '农历四月初七',
      limitInfo: '周末不限行',
      forecastDays: [],
      hourlyForecast: [],
      canvasWidth: 300,
      
      functionButtons: [
        { id: 1, name: '出行', icon: '/static/icons/general/car.png', type: 'transport' },
        { id: 2, name: '住宿', icon: '/static/icons/general/hotel.png', type: 'accommodation' },
        { id: 3, name: '美食', icon: '/static/icons/general/pizza.png', type: 'food' },
        { id: 4, name: '习俗', icon: '/static/icons/general/bagua.png', type: 'custom' },
        { id: 5, name: '购物', icon: '/static/icons/general/shopping.png', type: 'shopping' }
      ],
      banners: [
        { image: '/static/banners/banner1.jpg', title: 'Shopping Trap', desc: '特产固然吸引人，钱包更要保护好', type: 'tips' },
        { image: '/static/banners/banner2.jpg', title: 'Respecting', desc: '尊重他人也是尊重自己', type: 'tips' },
        { image: '/static/banners/banner3.jpg', title: 'Bomb Warning', desc: '请勿携带危险物品', type: 'tips' },
        { image: '/static/banners/banner4.jpg', title: 'Survival Kit', desc: '进入郊外必备', type: 'tips' },
        { image: '/static/banners/banner5.jpg', title: 'TAXI Trap', desc: '打车请到正规平台', type: 'tips' },
        { image: '/static/banners/banner6.jpg', title: 'Resist Scammers', desc: '抵制黄牛，从你我做起', type: 'tips' }
      ],
      transportModules: [
        { id: 1, name: '订购机票', icon: '/static/icons/general/airplane.png', target: '/pages/transport/transport?tab=airplane' },
        { id: 2, name: '火车高铁', icon: '/static/icons/general/train.png', target: '/pages/transport/transport?tab=train' },
        { id: 3, name: '大巴', icon: '/static/icons/general/bus.png', target: '/pages/transport/transport?tab=bus' },
        { id: 4, name: '租车/包车', icon: '/static/icons/general/car.png', target: '/pages/transport/transport?tab=car' },
        { id: 5, name: '公交/地铁', icon: '/static/icons/general/subway.png', target: '/pages/transport/transport?tab=public' }
      ],
      accommodationModules: [
        { id: 1, name: '酒店', icon: '/static/icons/general/hotel.png', target: '/pages/hotel/hotel' },
        { id: 2, name: '民宿', icon: '/static/icons/general/b&b.png', target: '/pages/homestay/homestay' }
      ],
      foodModules: [
        { id: 1, name: '餐厅', icon: '/static/icons/general/restaurant.png', target: '/pages/food/food?tab=restaurant' },
        { id: 2, name: '小吃街', icon: '/static/icons/general/snack.png', target: '/pages/food/food?tab=snack' }
      ],
      customModules: [
        { id: 1, name: '节日', icon: '/static/icons/general/gourd.png', target: '/pages/custom/custom?tab=festival' },
        { id: 2, name: '禁忌', icon: '/static/icons/general/bagua.png', target: '/pages/custom/custom?tab=taboo' }
      ],
      shoppingModules: [
        { id: 1, name: '线上购物', icon: '/static/icons/general/online-shopping.png', target: '/pages/shopping/shopping?tab=online' },
        { id: 2, name: '线下购物', icon: '/static/icons/general/offline-shopping.png', target: '/pages/shopping/shopping?tab=offline' }
      ]
    }
  },
  computed: {
    // 根据天气文字描述返回对应的动画样式类名
    animationClass() {
      const text = this.weatherInfo.weatherText || '';
      if (text.includes('雨') || text.includes('雪')) return 'weather-rainy';
      if (text.includes('多云')) return 'weather-cloudy';
      if (text.includes('阴')) return 'weather-overcast';
      return '';
    }
  },
  onLoad() {
    this.loadHotSearch()
    this.fetchWeather()
    this.getCanvasWidth()
  },
  onPullDownRefresh() {
    this.refreshData()
  },
  methods: {
    // 切换天气卡片显示
    toggleWeatherCard() {
      this.showWeatherCard = !this.showWeatherCard;
      // 当卡片显示时，延迟绘制折线图，确保canvas已渲染
      if (this.showWeatherCard && this.hourlyForecast.length) {
        this.$nextTick(() => {
          setTimeout(() => {
            this.drawTemperatureChart();
          }, 100);
        });
      }
    },
    getCanvasWidth() {
      const systemInfo = uni.getSystemInfoSync()
      this.canvasWidth = systemInfo.windowWidth - 80
    },
    drawTemperatureChart() {
      if (!this.hourlyForecast.length) return
      // 确保canvas已显示且尺寸正确
      const ctx = uni.createCanvasContext('tempTrendCanvas', this)
      const width = this.canvasWidth
      const height = 160
      const padding = { top: 20, bottom: 25, left: 25, right: 15 }
      const graphWidth = width - padding.left - padding.right
      const graphHeight = height - padding.top - padding.bottom
      
      const temps = this.hourlyForecast.map(h => h.temp)
      const minTemp = Math.min(...temps) - 1
      const maxTemp = Math.max(...temps) + 1
      const range = maxTemp - minTemp
      
      ctx.setFillStyle('#f8fbff')
      ctx.fillRect(0, 0, width, height)
      
      ctx.setStrokeStyle('#c0d0e8')
      ctx.setLineWidth(1)
      ctx.moveTo(padding.left, padding.top)
      ctx.lineTo(padding.left, height - padding.bottom)
      ctx.lineTo(width - padding.right, height - padding.bottom)
      ctx.stroke()
      
      ctx.setStrokeStyle('#e2e8f2')
      ctx.setLineWidth(0.5)
      for (let i = 0; i <= 4; i++) {
        const y = padding.top + (graphHeight / 4) * i
        ctx.moveTo(padding.left, y)
        ctx.lineTo(width - padding.right, y)
        ctx.stroke()
      }
      
      const stepX = graphWidth / (temps.length - 1)
      let points = []
      for (let i = 0; i < temps.length; i++) {
        const x = padding.left + i * stepX
        const y = padding.top + graphHeight - ((temps[i] - minTemp) / range) * graphHeight
        points.push({ x, y, temp: temps[i] })
      }
      
      ctx.beginPath()
      ctx.setStrokeStyle('#3a5bc7')
      ctx.setLineWidth(2.5)
      ctx.moveTo(points[0].x, points[0].y)
      for (let i = 1; i < points.length; i++) {
        ctx.lineTo(points[i].x, points[i].y)
      }
      ctx.stroke()
      
      points.forEach(point => {
        ctx.beginPath()
        ctx.setFillStyle('#ffffff')
        ctx.arc(point.x, point.y, 4, 0, 2 * Math.PI)
        ctx.fill()
        ctx.setFillStyle('#3a5bc7')
        ctx.arc(point.x, point.y, 2, 0, 2 * Math.PI)
        ctx.fill()
        ctx.setFillStyle('#2c3e8f')
        ctx.setFontSize(11)
        ctx.fillText(point.temp + '°', point.x - 12, point.y - 8)
      })
      
      ctx.setFillStyle('#7e92b5')
      ctx.setFontSize(10)
      for (let i = 0; i < temps.length; i += 3) {
        const x = padding.left + i * stepX
        const timeLabel = this.hourlyForecast[i].timeStr
        ctx.fillText(timeLabel, x - 12, height - padding.bottom + 12)
      }
      ctx.draw()
    },
    // 根据小时和天气文本，获取准确的小时天气图标
    getHourWeatherIcon(hour, baseWeatherText) {
      const isDaytime = hour >= 6 && hour < 18;
      const text = baseWeatherText || '';
      
      if (isDaytime) {
        if (text.includes('晴')) return '☀️';
        if (text.includes('多云')) return '⛅';
        if (text.includes('阴')) return '☁️';
        if (text.includes('雨')) return '🌧️';
        if (text.includes('雪')) return '❄️';
        return '🌤️';
      } else {
        if (text.includes('晴')) return '🌙';
        if (text.includes('多云')) return '☁️🌙';
        if (text.includes('阴')) return '☁️';
        if (text.includes('雨')) return '🌧️';
        if (text.includes('雪')) return '❄️';
        return '🌙';
      }
    },
    generateDetailedWeather(baseTemp, weatherText, cityName) {
      const delta = 4
      const high = Math.round(baseTemp + Math.random() * 3)
      const low = Math.round(baseTemp - Math.random() * 5)
      this.dayHighTemp = high
      this.dayLowTemp = low
      
      const speed = parseFloat(this.weatherInfo.windSpeed) || 5
      let level = 1
      if (speed < 1) level = 0
      else if (speed < 5) level = 1
      else if (speed < 11) level = 2
      else if (speed < 19) level = 3
      else level = 4
      this.windPowerLevel = level + '级'
      
      this.weatherInfo.aqi = Math.floor(Math.random() * 50) + 30
      this.airQualityText = this.weatherInfo.aqi <= 50 ? '优' : (this.weatherInfo.aqi <= 100 ? '良' : '轻度')
      this.uvIndex = baseTemp > 28 ? '强' : (baseTemp > 20 ? '中等' : '弱')
      
      this.sunriseTime = '06:' + (Math.floor(Math.random() * 30) + 10)
      this.sunsetTime = '18:' + (Math.floor(Math.random() * 40) + 20)
      
      const lunarDate = new Date()
      this.lunarInfo = `农历${lunarDate.getMonth()+1}月${lunarDate.getDate()}日`
      this.limitInfo = (new Date().getDay() % 6 === 0) ? '周末不限行' : '尾号限行'
      
      const weekDays = ['今天', '明天', '后天']
      this.forecastDays = weekDays.map((day, idx) => {
        const tempOffset = idx * (Math.random() * 2 - 1)
        const highT = Math.round(high + tempOffset)
        const lowT = Math.round(low + tempOffset - 2)
        let emoji = '☀️'
        if (weatherText.includes('云')) emoji = '⛅'
        if (weatherText.includes('雨')) emoji = '🌧️'
        if (weatherText.includes('雪')) emoji = '❄️'
        return {
          week: day,
          highTemp: highT,
          lowTemp: lowT,
          emoji: emoji
        }
      })
      
      // 生成小时预报
      const hours = []
      const nowHour = new Date().getHours()
      for (let i = 0; i < 12; i++) {
        const hourOffset = i
        const hourNum = (nowHour + hourOffset) % 24
        const timeStr = hourNum.toString().padStart(2, '0') + ':00'
        let tempVar = Math.sin((hourOffset - 6) * Math.PI / 8) * 3
        let hourTemp = Math.round(baseTemp + tempVar + (Math.random() * 2 - 1))
        hourTemp = Math.min(high + 2, Math.max(low - 2, hourTemp))
        const weatherEmoji = this.getHourWeatherIcon(hourNum, weatherText)
        hours.push({
          timeStr,
          temp: hourTemp,
          weatherEmoji
        })
      }
      this.hourlyForecast = hours
      
      // 如果当前卡片处于显示状态，则绘制图表
      if (this.showWeatherCard) {
        this.$nextTick(() => {
          setTimeout(() => {
            this.drawTemperatureChart()
          }, 100)
        })
      }
    },
    // 统一的天气请求方法（支持经纬度或ip）
    async requestWeather(locationParam) {
      const API_KEY = 'SX7GLnDy1bUNd-1XG'
      const url = `https://api.seniverse.com/v3/weather/now.json?key=${API_KEY}&location=${locationParam}&language=zh-Hans&unit=c`
      
      return new Promise((resolve, reject) => {
        uni.request({
          url: url,
          method: 'GET',
          success: (res) => {
            if (res.statusCode === 200 && res.data && res.data.results && res.data.results.length > 0) {
              const result = res.data.results[0]
              const location = result.location
              const now = result.now
              
              this.weatherInfo = {
                cityName: location.name,
                temp: Math.round(now.temperature),
                weatherText: now.text,
                weatherCode: now.code,
                humidity: now.humidity || Math.floor(Math.random() * 40 + 40),
                windSpeed: now.wind_speed || '10',
                windDir: now.wind_direction || '东南',
                feelsLike: now.feels_like ? Math.round(now.feels_like) : Math.round(now.temperature),
                updateTime: this.formatTime(new Date()),
                aqi: '--'
              }
              this.weatherIcon = this.getWeatherEmoji(now.code, now.text)
              this.generateDetailedWeather(this.weatherInfo.temp, this.weatherInfo.weatherText, this.weatherInfo.cityName)
              resolve()
            } else {
              reject(new Error('天气数据格式错误'))
            }
          },
          fail: (err) => {
            reject(err)
          }
        })
      })
    },
    // 获取定位并请求天气（优先定位，失败降级IP）
    async fetchWeather() {
      this.weatherLoading = true
      try {
        // 尝试获取用户地理位置
        const locationRes = await new Promise((resolve, reject) => {
          uni.getLocation({
            type: 'wgs84',
            success: resolve,
            fail: reject
          })
        })
        const { latitude, longitude } = locationRes
        const locationStr = `${latitude}:${longitude}`
        await this.requestWeather(locationStr)
      } catch (err) {
        console.warn('定位失败或用户拒绝，降级使用IP定位', err)
        uni.showToast({ title: '定位失败，使用网络定位', icon: 'none', duration: 1500 })
        try {
          await this.requestWeather('ip')
        } catch (ipErr) {
          console.error('IP天气请求也失败', ipErr)
          this.weatherLoading = false
          this.weatherInfo = {
            cityName: '',
            temp: '--',
            weatherText: '获取失败',
            weatherCode: '',
            humidity: '--',
            windSpeed: '--',
            windDir: '--',
            feelsLike: '--',
            updateTime: '',
            aqi: '--'
          }
          uni.showToast({ title: '天气加载失败，点击重试', icon: 'none' })
          return
        }
      }
      this.weatherLoading = false
    },
    refreshWeather() {
      this.fetchWeather()
    },
    getWeatherEmoji(code, text) {
      const codeMap = {
        '0': '☀️', '1': '⛅', '2': '☁️', '3': '🌦️', '4': '⛈️',
        '5': '🌨️', '6': '🌧️', '7': '🌨️', '8': '❄️', '9': '🌫️',
      }
      if (codeMap[code]) return codeMap[code]
      if (text.includes('晴')) return '☀️'
      if (text.includes('多云')) return '⛅'
      if (text.includes('阴')) return '☁️'
      if (text.includes('雨')) return '🌧️'
      if (text.includes('雪')) return '❄️'
      return '🌈'
    },
    formatTime(date) {
      return `${date.getHours().toString().padStart(2,'0')}:${date.getMinutes().toString().padStart(2,'0')}`
    },
    onSearch(keyword) {
      if (!keyword.trim()) return
      uni.navigateTo({ url: `/pages/search/result?keyword=${encodeURIComponent(keyword)}` })
    },
    onSearchFocus() {
      uni.navigateTo({ url: '/pages/search/search' })
    },
    loadHotSearch() {
      this.searchPlaceholder = '搜索 ' + this.getRandomHotSearch()
    },
    getRandomHotSearch() {
      const hotSearches = ['北京故宫', '上海外滩', '西安兵马俑', '成都火锅', '三亚海滩']
      return hotSearches[Math.floor(Math.random() * hotSearches.length)]
    },
    onFunctionButtonTap(item) {
      const mapping = {
        transport: '/pages/transport/transport?tab=airplane',
        accommodation: '/pages/hotel/hotel',
        custom: '/pages/custom/custom?tab=festival',
        food: '/pages/food/food?tab=restaurant',
        shopping: '/pages/shopping/shopping?tab=online'
      }
      uni.navigateTo({ url: mapping[item.type] })
    },
    onBannerTap(banner) {
      if (banner.target) uni.navigateTo({ url: banner.target })
      else uni.showToast({ title: banner.title, icon: 'none' })
    },
    navigateToAIChat() {
      uni.navigateTo({ url: '/pages/ai-chat/ai-chat' })
    },
    navigateToModule(moduleType) {
      const mapping = {
        transport: '/pages/transport/transport?tab=airplane',
        accommodation: '/pages/hotel/hotel',
        custom: '/pages/custom/custom?tab=festival',
        food: '/pages/food/food?tab=restaurant',
        shopping: '/pages/shopping/shopping?tab=online'
      }
      uni.navigateTo({ url: mapping[moduleType] })
    },
    navigateToSubModule(moduleType, subModule) {
      if (subModule.target) uni.navigateTo({ url: subModule.target })
      else uni.showToast({ title: `进入${subModule.name}`, icon: 'none' })
    },
    async refreshData() {
      try {
        await new Promise(resolve => setTimeout(resolve, 1000))
        this.loadHotSearch()
        this.fetchWeather()
        uni.stopPullDownRefresh()
        uni.showToast({ title: '刷新成功', icon: 'success' })
      } catch (error) {
        uni.stopPullDownRefresh()
        uni.showToast({ title: '刷新失败', icon: 'none' })
      }
    }
  }
}
</script>

<style scoped>
.travel-page {
  height: 100vh;
  background: linear-gradient(135deg, #f0f6ff 0%, #e8ecff 100%);
  display: flex;
  flex-direction: column;
}

.search-section {
  background: #fff;
  padding: 20rpx 30rpx;
  border-bottom: 1rpx solid #e0e8ff;
  box-shadow: 0 2rpx 10rpx rgba(184, 212, 255, 0.1);
}

.search-container {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.search-bar-flex {
  flex: 1;
}

/* 天气区域 - 相对定位容器 */
.weather-area {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #f0f6ff, #ffffff);
  padding: 12rpx 24rpx;
  border-radius: 48rpx;
  border: 1rpx solid #e0e8ff;
  box-shadow: 0 2rpx 8rpx rgba(184, 212, 255, 0.2);
  transition: all 0.3s ease;
  cursor: pointer;
  min-width: 240rpx;
}

.weather-main {
  display: flex;
  align-items: center;
  gap: 12rpx;
  flex: 1;
}

.weather-refresh {
  margin-left: 12rpx;
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #eef3ff;
  transition: all 0.2s;
}

.weather-refresh:active {
  transform: rotate(30deg);
}

.refresh-icon {
  font-size: 32rpx;
  color: #3a5bc7;
  font-weight: bold;
}

.weather-emoji {
  font-size: 40rpx;
}

.weather-text {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  line-height: 1.2;
}

.city-name {
  font-size: 24rpx;
  font-weight: 600;
  color: #3a5bc7;
}

.temp-info {
  font-size: 28rpx;
  font-weight: bold;
  color: #3a5bc7;
}

.weather-desc {
  font-size: 22rpx;
  color: #7a8fcf;
  margin-left: 8rpx;
  background: #eef3ff;
  padding: 4rpx 12rpx;
  border-radius: 20rpx;
}

/* 天气卡片 - 点击切换显示，适配移动端 */
.weather-card {
  position: absolute;
  top: calc(100% + 15rpx);
  left: 0;
  right: 0;
  margin: 0 auto;
  width: 640rpx;
  max-width: calc(100vw - 60rpx);
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20rpx);
  border-radius: 32rpx;
  padding: 28rpx;
  box-shadow: 0 30rpx 50rpx rgba(0, 0, 0, 0.2);
  border: 1rpx solid rgba(184, 212, 255, 0.8);
  z-index: 1000;
  transition: all 0.3s cubic-bezier(0.2, 0.9, 0.4, 1.1);
  overflow: hidden;
}

/* 动态背景层 - 绝对定位，不干扰交互 */
.weather-animation-layer {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 1;
  border-radius: 32rpx;
  overflow: hidden;
}

/* 卡片主要内容需要浮在动态层之上 */
.card-header,
.card-main-temp,
.card-details-grid,
.forecast-3days,
.hourly-section {
  position: relative;
  z-index: 2;
}

/* 雨天：雨滴滑落效果 */
.weather-animation-layer.weather-rainy::before,
.weather-animation-layer.weather-rainy::after {
  content: '';
  position: absolute;
  top: -20%;
  left: 0;
  width: 100%;
  height: 120%;
  background: repeating-linear-gradient(
    to bottom,
    rgba(255, 255, 255, 0.3) 0px,
    rgba(255, 255, 255, 0.3) 2px,
    transparent 2px,
    transparent 8px
  );
  animation: rainDrop 1.2s linear infinite;
  pointer-events: none;
}
.weather-animation-layer.weather-rainy::after {
  background: repeating-linear-gradient(
    to bottom,
    rgba(200, 220, 255, 0.4) 0px,
    rgba(200, 220, 255, 0.4) 1px,
    transparent 1px,
    transparent 6px
  );
  animation-duration: 0.8s;
  animation-delay: -0.4s;
}
@keyframes rainDrop {
  0% {
    transform: translateY(-30%);
  }
  100% {
    transform: translateY(30%);
  }
}

/* 多云：云朵飘过动画 */
.weather-animation-layer.weather-cloudy {
  background: transparent;
}
.weather-animation-layer.weather-cloudy::before,
.weather-animation-layer.weather-cloudy::after {
  content: '';
  position: absolute;
  background: rgba(255, 255, 255, 0.65);
  border-radius: 50%;
  animation: cloudFloat 24s linear infinite;
}
.weather-animation-layer.weather-cloudy::before {
  width: 120rpx;
  height: 60rpx;
  top: 15%;
  left: -60rpx;
  box-shadow: 30rpx 10rpx 0 0 rgba(255,255,255,0.5), 60rpx 0 0 0 rgba(255,255,255,0.3);
  border-radius: 60rpx;
  animation-duration: 18s;
  animation-delay: 0s;
}
.weather-animation-layer.weather-cloudy::after {
  width: 90rpx;
  height: 45rpx;
  bottom: 20%;
  right: -45rpx;
  box-shadow: -20rpx 10rpx 0 0 rgba(255,255,255,0.5), -50rpx -5rpx 0 0 rgba(255,255,255,0.3);
  border-radius: 45rpx;
  animation-duration: 22s;
  animation-delay: -5s;
}
@keyframes cloudFloat {
  0% {
    transform: translateX(0) translateY(0);
    opacity: 0;
  }
  10% {
    opacity: 0.8;
  }
  90% {
    opacity: 0.8;
  }
  100% {
    transform: translateX(calc(100% + 200rpx)) translateY(-20rpx);
    opacity: 0;
  }
}

/* 阴天：灰色背景动态（缓慢流动的光影） */
.weather-animation-layer.weather-overcast {
  background: linear-gradient(120deg, rgba(100,110,130,0.2), rgba(70,80,100,0.15), rgba(100,110,130,0.2));
  background-size: 200% 200%;
  animation: overcastFlow 12s ease infinite;
}
@keyframes overcastFlow {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 20rpx;
  border-bottom: 1rpx solid #eef2ff;
  padding-bottom: 16rpx;
}

.card-city {
  font-size: 36rpx;
  font-weight: 800;
  color: #1e2f6e;
  margin-right: 16rpx;
}

.card-time {
  font-size: 22rpx;
  color: #8a9bc1;
}

.publish-tip {
  background: #eef3ff;
  padding: 6rpx 16rpx;
  border-radius: 40rpx;
  font-size: 20rpx;
  color: #3a5bc7;
}

.card-main-temp {
  display: flex;
  align-items: baseline;
  gap: 20rpx;
  margin-bottom: 24rpx;
}

.big-temp {
  font-size: 68rpx;
  font-weight: 800;
  color: #1e2f6e;
}

.temp-range {
  display: flex;
  flex-direction: column;
}

.range-text {
  font-size: 24rpx;
  color: #5e73a8;
}

.weather-status {
  font-size: 22rpx;
  background: #eef3ff;
  padding: 4rpx 12rpx;
  border-radius: 24rpx;
  display: inline-block;
  margin-top: 6rpx;
  color: #3a5bc7;
}

.card-details-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20rpx;
  background: #f8fbff;
  padding: 20rpx;
  border-radius: 28rpx;
  margin-bottom: 24rpx;
}

.detail-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
}

.detail-label {
  font-size: 22rpx;
  color: #7e92b5;
}

.detail-value {
  font-size: 26rpx;
  font-weight: 600;
  color: #2c3e8f;
}

.forecast-3days {
  display: flex;
  justify-content: space-around;
  background: #ffffffd9;
  border-radius: 24rpx;
  padding: 16rpx 0;
  margin-bottom: 24rpx;
  border: 1rpx solid #e0e8ff;
}

.forecast-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
}

.forecast-week {
  font-size: 24rpx;
  font-weight: 600;
  color: #3a5bc7;
}

.forecast-emoji {
  font-size: 36rpx;
}

.forecast-temp {
  font-size: 24rpx;
  color: #2c3e8f;
}

.hourly-section {
  margin-top: 8rpx;
}

.hourly-title {
  font-size: 26rpx;
  font-weight: 600;
  color: #2c3e8f;
  margin-bottom: 12rpx;
}

.trend-canvas {
  width: 100%;
  height: 160px;
  background: #f8fbff;
  border-radius: 20rpx;
  margin-bottom: 12rpx;
}

.hourly-scroll {
  white-space: nowrap;
  width: 100%;
}

.hourly-list {
  display: inline-flex;
  gap: 24rpx;
  padding: 8rpx 0;
}

.hour-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 80rpx;
}

.hour-time {
  font-size: 22rpx;
  color: #7e92b5;
}

.hour-temp {
  font-size: 28rpx;
  font-weight: bold;
  color: #1e2f6e;
  margin: 8rpx 0;
}

.hour-weather {
  font-size: 32rpx;
}

.loading-area, .error-area {
  justify-content: center;
  background: #f5f9ff;
}

.search-icon {
  width: 40rpx;
  height: 40rpx;
  margin-right: 20rpx;
}

.function-buttons {
  background: #fff;
  padding: 30rpx 0;
  border-bottom: 1rpx solid #e0e8ff;
}

.buttons-scroll {
  white-space: nowrap;
  width: 100%;
}

.button-item {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  width: 140rpx;
  margin: 0 20rpx;
  transition: all 0.3s ease;
}

.button-item:active {
  transform: scale(0.95);
}

.button-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 20rpx;
  background: linear-gradient(135deg, #b8d4ff, #bcc4e8);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16rpx;
  box-shadow: 0 4rpx 12rpx rgba(184, 212, 255, 0.4);
}

.icon-image {
  width: 65rpx;
  height: 65rpx;
}

.button-text {
  font-size: 24rpx;
  color: #3a5bc7;
  font-weight: 500;
}

.banner-section {
  padding: 30rpx;
  background: #fff;
}

.banner-swiper {
  height: 300rpx;
  border-radius: 20rpx;
  overflow: hidden;
  box-shadow: 0 6rpx 20rpx rgba(184, 212, 255, 0.3);
}

.banner-image {
  width: 100%;
  height: 100%;
}

.banner-mask {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  padding: 40rpx 30rpx 20rpx;
  color: #fff;
}

.banner-title {
  font-size: 32rpx;
  font-weight: 600;
  display: block;
  margin-bottom: 8rpx;
}

.banner-desc {
  font-size: 24rpx;
  opacity: 0.9;
}

.ai-assistant-section {
  padding: 0 30rpx 20rpx;
  background: #fff;
}

.ai-assistant-card {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #f8fbff 0%, #edf2ff 100%);
  border-radius: 20rpx;
  padding: 30rpx;
  border: 1rpx solid #e0e8ff;
  box-shadow: 0 4rpx 16rpx rgba(184, 212, 255, 0.3);
  transition: all 0.3s ease;
}

.ai-assistant-card:active {
  transform: scale(0.98);
}

.ai-avatar {
  position: relative;
  width: 100rpx;
  height: 100rpx;
  margin-right: 24rpx;
}

.avatar-image {
  width: 100rpx;
  height: 100rpx;
  border-radius: 20rpx;
  background: linear-gradient(135deg, #b8d4ff, #bcc4e8);
  box-shadow: 0 4rpx 12rpx rgba(184, 212, 255, 0.4);
}

.ai-status {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 20rpx;
  height: 20rpx;
  background: #52c41a;
  border: 3rpx solid #fff;
  border-radius: 50%;
}

.ai-content {
  flex: 1;
}

.ai-header {
  display: flex;
  align-items: center;
  margin-bottom: 12rpx;
}

.ai-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #3a5bc7;
  margin-right: 16rpx;
}

.ai-tag {
  background: #52c41a;
  color: #fff;
  font-size: 20rpx;
  padding: 4rpx 12rpx;
  border-radius: 20rpx;
}

.ai-desc {
  font-size: 24rpx;
  color: #666;
  line-height: 1.4;
}

.ai-arrow {
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  background: #e8ecff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.arrow-icon {
  font-size: 32rpx;
  color: #3a5bc7;
  font-weight: bold;
}

.function-modules {
  flex: 1;
  background: transparent;
}

.modules-scroll {
  height: 100%;
  padding: 0 30rpx;
}

.module-section {
  background: linear-gradient(135deg, #ffffff 0%, #f8fbff 100%);
  margin: 30rpx 0;
  border-radius: 20rpx;
  overflow: hidden;
  box-shadow: 0 6rpx 20rpx rgba(184, 212, 255, 0.3);
  border: 1rpx solid #e0e8ff;
}

.module-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #e0e8ff;
  background: #fff;
}

.module-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #3a5bc7;
}

.module-more {
  font-size: 26rpx;
  color: #8a9bc1;
}

.module-content {
  padding: 20rpx;
  background: #fff;
}

.sub-modules-scroll {
  white-space: nowrap;
  width: 100%;
}

.sub-module {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  width: 140rpx;
  margin: 0 15rpx;
  transition: all 0.3s ease;
}

.sub-module:active {
  transform: scale(0.95);
}

.sub-icon {
  width: 80rpx;
  height: 80rpx;
  background: linear-gradient(135deg, #f5f9ff 0%, #edf2ff 100%);
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16rpx;
  border: 1rpx solid #e0e8ff;
}

.sub-icon image {
  width: 65rpx;
  height: 65rpx;
}

.sub-text {
  font-size: 24rpx;
  color: #5a7bdb;
  text-align: center;
  font-weight: 500;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.module-section {
  animation: fadeInUp 0.6s ease forwards;
}

@media (max-width: 750rpx) {
  .weather-card {
    width: 560rpx;
    max-width: calc(100vw - 60rpx);
    left: 0;
    right: 0;
    margin: 0 auto;
  }
  .card-details-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>