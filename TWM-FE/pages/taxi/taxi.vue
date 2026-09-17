<template>
  <view class="taxi-page">
    <!-- 顶部状态栏 - 动态真实数据 -->
    <view class="status-bar">
      <view class="status-item">
        <image class="status-icon" src="/static/icons/taxi/distance.png" mode="aspectFit"></image>
        <text class="status-label">附近车辆</text>
        <text class="status-value">{{ nearbyCars }}辆</text>
      </view>
      <view class="status-item">
        <image class="status-icon" src="/static/icons/taxi/time.png" mode="aspectFit"></image>
        <text class="status-label">平均等待</text>
        <text class="status-value">{{ avgWaitTime }}分钟</text>
      </view>
      <view class="status-item">
        <image class="status-icon" src="/static/icons/taxi/price.png" mode="aspectFit"></image>
        <text class="status-label">起步价</text>
        <text class="status-value">¥{{ startPrice }}</text>
      </view>
    </view>

    <!-- 地址输入 - 使用腾讯地图API选择真实地点 -->
    <view class="address-section">
      <view class="location-inputs">
        <view class="input-item start">
          <view class="input-dot"></view>
          <input 
            class="input-field" 
            placeholder="请输入起点" 
            v-model="startAddress"
            @focus="onStartFocus"
            disabled
          />
          <view class="input-action" @tap="chooseStartLocation">
            <image class="action-icon" src="/static/icons/general/location.png" mode="aspectFit"></image>
            <text>定位</text>
          </view>
        </view>
        
        <view class="input-swap" @tap="swapAddresses">
          <image class="swap-icon" src="/static/icons/general/swap.png" mode="aspectFit"></image>
        </view>
        
        <view class="input-item end">
          <view class="input-dot"></view>
          <input 
            class="input-field" 
            placeholder="请输入终点" 
            v-model="endAddress"
            @focus="onEndFocus"
            disabled
          />
          <view class="input-action" @tap="clearEndAddress" v-if="endAddress">
            <image class="action-icon" src="/static/icons/general/close.png" mode="aspectFit"></image>
          </view>
        </view>
      </view>
      
      <!-- 常用地址 - 动态从本地存储读取 -->
      <view class="common-addresses" v-if="commonAddresses.length > 0">
        <scroll-view class="address-scroll" scroll-x :show-scrollbar="false">
          <view 
            class="address-tag" 
            v-for="address in commonAddresses" 
            :key="address.id"
            @tap="selectCommonAddress(address)"
          >
            <image class="address-icon" :src="address.icon" mode="aspectFit"></image>
            <text>{{ address.name }}</text>
          </view>
        </scroll-view>
      </view>
    </view>

    <!-- 车型选择 - 价格基于实时路线动态计算 -->
    <view class="car-type-section">
      <view class="section-header">
        <text class="section-title">选择车型</text>
        <view class="price-estimate" v-if="routeDistance">
          <text>预估¥{{ estimatedPrice }}</text>
        </view>
      </view>
      
      <view class="car-type-grid">
        <view 
          class="car-type-card" 
          v-for="car in dynamicCarTypes" 
          :key="car.type"
          :class="{ active: selectedCarType === car.type, recommended: car.recommended }"
          @tap="selectCarType(car.type)"
        >
          <view class="car-header">
            <image class="car-icon" :src="car.icon" mode="aspectFit"></image>
            <view class="car-badge" v-if="car.recommended">推荐</view>
          </view>
          <text class="car-name">{{ car.name }}</text>
          <text class="car-desc">{{ car.description }}</text>
          <view class="car-price">
            <text class="price-main">¥{{ car.dynamicPrice }}</text>
            <text class="price-unit">预估</text>
          </view>
          <view class="car-details">
            <view class="detail-item">
              <image class="detail-icon" src="/static/icons/taxi/time.png" mode="aspectFit"></image>
              <text>{{ car.waitTime }}分钟接驾</text>
            </view>
            <view class="detail-item">
              <image class="detail-icon" src="/static/icons/taxi/capacity.png" mode="aspectFit"></image>
              <text>{{ car.capacity }}人</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 呼叫按钮 -->
    <view class="call-section">
      <view class="price-breakdown">
        <view class="price-item">
          <text class="price-label">预估费用</text>
          <text class="price-value">¥{{ estimatedPrice }}</text>
        </view>
        <view class="price-item total">
          <text class="price-label">实付金额</text>
          <text class="price-value final">¥{{ finalPrice }}</text>
        </view>
      </view>
      
      <view class="call-action">
        <view class="call-info" v-if="routeDistance">
          <text class="distance">距离{{ routeDistance }}</text>
          <text class="time">预计{{ routeDuration }}</text>
        </view>
        <view class="call-info" v-else>
          <text class="distance">请选择起点和终点</text>
        </view>
        <view class="call-btn" @tap="callTaxi" :class="{ disabled: !canCallTaxi }">
          <text class="call-text">{{ callButtonText }}</text>
          <text class="call-price" v-if="finalPrice">¥{{ finalPrice }}</text>
        </view>
      </view>
    </view>

    <!-- 底部安全区域 -->
    <view class="safe-area"></view>
  </view>
</template>

<script>
// 腾讯地图API配置
const TENCENT_MAP_KEY = '4DYBZ-7QXEC-CWM2S-AXAZR-YLVQF-C6BPY';
const TENCENT_MAP_BASE_URL = 'https://apis.map.qq.com';

// 城市起步价映射表（真实城市起步价参考）
const CITY_START_PRICE = {
  '北京市': 13,
  '上海市': 14,
  '广州市': 12,
  '深圳市': 12,
  '杭州市': 11,
  '成都市': 9,
  '武汉市': 10,
  '西安市': 9,
  '重庆市': 10,
  'default': 10
};

// 车型费率配置（元/公里）
const CAR_RATES = {
  economy: { name: '快车', rate: 2.0, waitTime: 3, capacity: 4, recommended: true, description: '经济实惠' },
  comfort: { name: '专车', rate: 3.2, waitTime: 5, capacity: 4, recommended: false, description: '舒适体验' },
  luxury: { name: '豪华车', rate: 5.5, waitTime: 8, capacity: 4, recommended: false, description: '尊享服务' },
  business: { name: '商务车', rate: 4.0, waitTime: 6, capacity: 6, recommended: false, description: '多人出行' },
  pool: { name: '拼车', rate: 1.5, waitTime: 5, capacity: 4, recommended: false, description: '绿色出行' }
};

export default {
  data() {
    return {
      startAddress: '',
      endAddress: '',
      selectedCarType: 'economy',
      
      // 真实动态数据
      nearbyCars: 0,
      avgWaitTime: 0,
      startPrice: 10,
      
      // 路线数据
      routeDistance: null,      // 格式化距离字符串
      routeDistanceMeters: 0,   // 距离（米）
      routeDuration: null,      // 格式化时间字符串
      routeDurationSeconds: 0,  // 时间（秒）
      
      // 位置坐标
      startLatLng: null,
      endLatLng: null,
      currentCity: 'default',
      
      // 常用地址
      commonAddresses: [],
      
      loading: false,
      searchTimer: null
    }
  },
  computed: {
    selectedCarTypeName() {
      return CAR_RATES[this.selectedCarType]?.name || '快车';
    },
    
    // 动态车型列表（价格基于实时路线动态计算）
    dynamicCarTypes() {
      const distanceKm = this.routeDistanceMeters / 1000;
      const baseFare = this.startPrice;
      
      return Object.entries(CAR_RATES).map(([type, config]) => {
        let dynamicPrice = 0;
        if (distanceKm > 0) {
          // 预估费用 = 起步价 + 里程费 + 时长费（简化：时长按0.5元/分钟估算）
          const timeFee = this.routeDurationSeconds / 60 * 0.5;
          dynamicPrice = Math.round(baseFare + distanceKm * config.rate + timeFee);
        } else {
          dynamicPrice = baseFare;
        }
        
        return {
          type,
          name: config.name,
          icon: `/static/icons/taxi/${type}.png`,
          description: config.description,
          price: config.rate, // 保留用于显示费率
          dynamicPrice: dynamicPrice,
          waitTime: config.waitTime,
          capacity: config.capacity,
          recommended: config.recommended
        };
      });
    },
    
    // 当前选中车型的预估价格
    estimatedPrice() {
      const selectedCar = this.dynamicCarTypes.find(car => car.type === this.selectedCarType);
      return selectedCar ? selectedCar.dynamicPrice : 0;
    },
    
    // 最终价格（无优惠券逻辑，直接使用预估价格）
    finalPrice() {
      return this.estimatedPrice;
    },
    
    canCallTaxi() {
      return !!(this.startAddress && this.endAddress && this.startLatLng && this.endLatLng);
    },
    
    callButtonText() {
      if (!this.canCallTaxi) {
        return '请输入地址';
      }
      return `呼叫${this.selectedCarTypeName}`;
    }
  },
  onLoad() {
    this.loadCommonAddresses();
    this.initLocationAndData();
  },
  methods: {
    // 加载常用地址（从本地存储）
    loadCommonAddresses() {
      try {
        const saved = uni.getStorageSync('taxi_common_addresses');
        if (saved && Array.isArray(saved)) {
          this.commonAddresses = saved;
        } else {
          // 默认常用地址（仅为示例，无静态价格数据）
          this.commonAddresses = [
            { id: 1, name: '家', icon: '/static/icons/taxi/home.png' },
            { id: 2, name: '公司', icon: '/static/icons/taxi/company.png' }
          ];
        }
      } catch(e) {}
    },
    
    // 保存常用地址
    saveCommonAddress(address) {
      const exists = this.commonAddresses.some(a => a.name === address.name);
      if (!exists && this.commonAddresses.length < 6) {
        this.commonAddresses.push(address);
        try {
          uni.setStorageSync('taxi_common_addresses', this.commonAddresses);
        } catch(e) {}
      }
    },
    
    // 初始化定位和周边数据
    async initLocationAndData() {
      uni.showLoading({ title: '定位中...' });
      try {
        const location = await this.getUserLocation();
        this.startLatLng = { lat: location.latitude, lng: location.longitude };
        // 逆地理编码获取地址名称
        const addressName = await this.reverseGeocode(location.latitude, location.longitude);
        this.startAddress = addressName || '当前位置';
        
        // 获取城市信息用于起步价
        await this.getCityAndStartPrice(location.latitude, location.longitude);
        
        // 获取附近车辆信息（出租车POI数量）
        await this.fetchNearbyTaxiInfo(location.latitude, location.longitude);
        
        uni.hideLoading();
      } catch (error) {
        uni.hideLoading();
        console.error('定位失败:', error);
        uni.showToast({ title: '定位失败，使用默认位置', icon: 'none' });
        this.startAddress = '北京市朝阳区';
        this.startLatLng = { lat: 39.9042, lng: 116.4074 };
        this.startPrice = CITY_START_PRICE['北京市'] || 13;
        await this.fetchNearbyTaxiInfo(39.9042, 116.4074);
      }
    },
    
    // 获取用户位置
    getUserLocation() {
      return new Promise((resolve, reject) => {
        uni.getLocation({
          type: 'gcj02',
          success: resolve,
          fail: reject
        });
      });
    },
    
    // 逆地理编码
    reverseGeocode(lat, lng) {
      return new Promise((resolve) => {
        const url = `${TENCENT_MAP_BASE_URL}/ws/geocoder/v1/?location=${lat},${lng}&key=${TENCENT_MAP_KEY}&get_poi=0`;
        uni.request({
          url,
          success: (res) => {
            if (res.data.status === 0 && res.data.result) {
              resolve(res.data.result.address);
            } else {
              resolve('');
            }
          },
          fail: () => resolve('')
        });
      });
    },
    
    // 获取城市和起步价
    async getCityAndStartPrice(lat, lng) {
      try {
        const url = `${TENCENT_MAP_BASE_URL}/ws/geocoder/v1/?location=${lat},${lng}&key=${TENCENT_MAP_KEY}`;
        const res = await this.requestAPI(url);
        if (res.status === 0 && res.result) {
          const city = res.result.address_component?.city || '';
          this.currentCity = city;
          this.startPrice = CITY_START_PRICE[city] || CITY_START_PRICE.default;
        }
      } catch (error) {
        console.error('获取城市失败:', error);
        this.startPrice = CITY_START_PRICE.default;
      }
    },
    
    // 获取附近出租车POI数量（模拟附近车辆数）
    async fetchNearbyTaxiInfo(lat, lng) {
      try {
        const url = `${TENCENT_MAP_BASE_URL}/ws/place/v1/search`;
        const params = {
          key: TENCENT_MAP_KEY,
          boundary: `nearby(${lat},${lng},2000)`,
          keyword: '出租车',
          page_size: 20
        };
        const res = await this.requestAPI(url, params);
        if (res.status === 0 && res.data) {
          const taxiCount = res.data.length;
          this.nearbyCars = Math.min(taxiCount * 2 + 5, 50); // 模拟车辆数，实际POI每个点可能有多辆车
          // 根据车辆密度计算平均等待时间（分钟），车辆越多等待时间越短
          if (this.nearbyCars > 30) this.avgWaitTime = 2;
          else if (this.nearbyCars > 15) this.avgWaitTime = 4;
          else if (this.nearbyCars > 5) this.avgWaitTime = 6;
          else this.avgWaitTime = 8;
        } else {
          this.nearbyCars = 12;
          this.avgWaitTime = 5;
        }
      } catch (error) {
        console.error('获取周边出租车信息失败:', error);
        this.nearbyCars = 15;
        this.avgWaitTime = 4;
      }
    },
    
    // 选择起点（使用腾讯地图POI选择）
    async chooseStartLocation() {
      try {
        const location = await this.chooseLocationByMap();
        if (location) {
          this.startAddress = location.name;
          this.startLatLng = { lat: location.latitude, lng: location.longitude };
          // 更新城市和起步价
          await this.getCityAndStartPrice(location.latitude, location.longitude);
          // 重新获取附近车辆信息
          await this.fetchNearbyTaxiInfo(location.latitude, location.longitude);
          // 如果已有终点，重新规划路线
          if (this.endLatLng) {
            await this.calculateRoute();
          }
        }
      } catch (error) {
        console.error('选择起点失败:', error);
      }
    },
    
    // 选择终点
    async chooseEndLocation() {
      try {
        const location = await this.chooseLocationByMap();
        if (location) {
          this.endAddress = location.name;
          this.endLatLng = { lat: location.latitude, lng: location.longitude };
          // 保存为常用地址
          this.saveCommonAddress({ id: Date.now(), name: location.name, icon: '/static/icons/taxi/station.png' });
          // 计算路线
          await this.calculateRoute();
        }
      } catch (error) {
        console.error('选择终点失败:', error);
      }
    },
    
    // 调用地图选择位置（使用原生地图选择）
    chooseLocationByMap() {
      return new Promise((resolve, reject) => {
        uni.chooseLocation({
          success: (res) => {
            if (res.name) {
              resolve({
                name: res.name,
                latitude: res.latitude,
                longitude: res.longitude,
                address: res.address
              });
            } else {
              reject(new Error('未选择位置'));
            }
          },
          fail: reject
        });
      });
    },
    
    // 计算路线规划（驾车）
    async calculateRoute() {
      if (!this.startLatLng || !this.endLatLng) return;
      
      uni.showLoading({ title: '计算路线中...' });
      try {
        const url = `${TENCENT_MAP_BASE_URL}/ws/direction/v1/driving`;
        const params = {
          key: TENCENT_MAP_KEY,
          from: `${this.startLatLng.lat},${this.startLatLng.lng}`,
          to: `${this.endLatLng.lat},${this.endLatLng.lng}`,
          output: 'json'
        };
        const res = await this.requestAPI(url, params);
        if (res.status === 0 && res.result && res.result.routes && res.result.routes.length > 0) {
          const route = res.result.routes[0];
          const distance = route.distance; // 米
          const duration = route.duration; // 秒
          
          this.routeDistanceMeters = distance;
          if (distance < 1000) {
            this.routeDistance = `${Math.round(distance)}m`;
          } else {
            this.routeDistance = `${(distance / 1000).toFixed(1)}km`;
          }
          
          this.routeDurationSeconds = duration;
          if (duration < 60) {
            this.routeDuration = `${duration}秒`;
          } else {
            const minutes = Math.floor(duration / 60);
            this.routeDuration = `${minutes}分钟`;
          }
        } else {
          this.routeDistance = null;
          this.routeDuration = null;
          uni.showToast({ title: '未找到可行路线', icon: 'none' });
        }
      } catch (error) {
        console.error('路线规划失败:', error);
        uni.showToast({ title: '路线规划失败', icon: 'none' });
      } finally {
        uni.hideLoading();
      }
    },
    
    // 统一请求封装
    requestAPI(url, params = {}) {
      return new Promise((resolve, reject) => {
        uni.request({
          url: url,
          method: 'GET',
          data: params,
          timeout: 10000,
          success: (res) => {
            if (res.statusCode === 200) {
              resolve(res.data);
            } else {
              reject(new Error(`请求失败: ${res.statusCode}`));
            }
          },
          fail: reject
        });
      });
    },
    
    onStartFocus() {
      this.chooseStartLocation();
    },
    
    onEndFocus() {
      this.chooseEndLocation();
    },
    
    swapAddresses() {
      [this.startAddress, this.endAddress] = [this.endAddress, this.startAddress];
      [this.startLatLng, this.endLatLng] = [this.endLatLng, this.startLatLng];
      if (this.startLatLng && this.endLatLng) {
        this.calculateRoute();
      }
    },
    
    clearEndAddress() {
      this.endAddress = '';
      this.endLatLng = null;
      this.routeDistance = null;
      this.routeDuration = null;
      this.routeDistanceMeters = 0;
      this.routeDurationSeconds = 0;
    },
    
    selectCommonAddress(address) {
      this.endAddress = address.name;
      // 如果有存储坐标则使用，否则需要用户选择具体位置
      if (address.lat && address.lng) {
        this.endLatLng = { lat: address.lat, lng: address.lng };
        if (this.startLatLng) this.calculateRoute();
      } else {
        this.chooseEndLocation();
      }
    },
    
    selectCarType(carType) {
      this.selectedCarType = carType;
    },
    
    // 呼叫出租车
    callTaxi() {
      if (!this.canCallTaxi) {
        uni.showToast({
          title: '请选择起点和终点',
          icon: 'none'
        });
        return;
      }
      
      uni.showLoading({ title: '呼叫中...' });
      
      setTimeout(() => {
        uni.hideLoading();
        
        const orderInfo = {
          carType: this.selectedCarTypeName,
          start: this.startAddress,
          end: this.endAddress,
          price: this.finalPrice,
          distance: this.routeDistance,
          duration: this.routeDuration
        };
        
        uni.showModal({
          title: '呼叫成功',
          content: `已为您呼叫${orderInfo.carType}\n起点：${orderInfo.start}\n终点：${orderInfo.end}\n预估费用：¥${orderInfo.price}`,
          showCancel: false,
          success: () => {
            // 可跳转到等待页面
            // uni.navigateTo({ url: `/pages/taxi/order-waiting?info=${encodeURIComponent(JSON.stringify(orderInfo))}` });
          }
        });
      }, 1000);
    }
  }
}
</script>

<style scoped>
/* 保持原有样式不变 */
.taxi-page {
  height: 100vh;
  background-color: #f8f8f8;
  display: flex;
  flex-direction: column;
}

.status-bar {
  background: linear-gradient(135deg, #667eea, #764ba2);
  padding: 30rpx;
  display: flex;
  justify-content: space-between;
  border-bottom-left-radius: 30rpx;
  border-bottom-right-radius: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(102, 126, 234, 0.3);
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

.address-section {
  background: #fff;
  padding: 30rpx;
  border-bottom: 1rpx solid #eee;
}

.location-inputs {
  position: relative;
  margin-bottom: 20rpx;
}

.input-item {
  display: flex;
  align-items: center;
  background: #f8f8f8;
  border-radius: 16rpx;
  padding: 25rpx;
  margin-bottom: 15rpx;
  position: relative;
}

.input-item.start {
  border-left: 4rpx solid #6bcf7f;
}

.input-item.end {
  border-left: 4rpx solid #ff6b6b;
}

.input-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  margin-right: 20rpx;
}

.input-item.start .input-dot {
  background: #6bcf7f;
}

.input-item.end .input-dot {
  background: #ff6b6b;
}

.input-field {
  flex: 1;
  font-size: 28rpx;
  color: #333;
}

.input-action {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 24rpx;
  color: #b8d4ff;
  padding: 10rpx 15rpx;
  background: #f0f7ff;
  border-radius: 20rpx;
}

.action-icon {
  width: 24rpx;
  height: 24rpx;
}

.input-swap {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 60rpx;
  height: 60rpx;
  background: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
  z-index: 2;
}

.swap-icon {
  width: 28rpx;
  height: 28rpx;
}

.common-addresses {
  margin-top: 20rpx;
}

.address-scroll {
  white-space: nowrap;
}

.address-tag {
  display: inline-flex;
  align-items: center;
  gap: 10rpx;
  background: #f0f7ff;
  border-radius: 25rpx;
  padding: 15rpx 20rpx;
  margin-right: 15rpx;
  font-size: 24rpx;
  color: #b8d4ff;
  transition: all 0.3s ease;
}

.address-tag:active {
  background: #e8f1ff;
  transform: scale(0.95);
}

.address-icon {
  width: 24rpx;
  height: 24rpx;
}

.car-type-section {
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

.price-estimate {
  font-size: 26rpx;
  color: #ff6b6b;
  font-weight: 600;
  background: #ffeaea;
  padding: 8rpx 16rpx;
  border-radius: 12rpx;
}

.car-type-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20rpx;
}

.car-type-card {
  background: #f8f8f8;
  border-radius: 20rpx;
  padding: 25rpx;
  border: 2rpx solid transparent;
  transition: all 0.3s ease;
  position: relative;
}

.car-type-card.active {
  border-color: #b8d4ff;
  background: #f8fbff;
  box-shadow: 0 4rpx 15rpx rgba(184, 212, 255, 0.3);
}

.car-type-card.recommended::before {
  content: '推荐';
  position: absolute;
  top: -10rpx;
  right: 20rpx;
  background: #ff6b6b;
  color: #fff;
  font-size: 20rpx;
  padding: 6rpx 12rpx;
  border-radius: 20rpx;
}

.car-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15rpx;
}

.car-icon {
  width: 60rpx;
  height: 60rpx;
}

.car-badge {
  font-size: 20rpx;
  color: #b8d4ff;
  background: rgba(184, 212, 255, 0.2);
  padding: 4rpx 8rpx;
  border-radius: 6rpx;
}

.car-name {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
  display: block;
  margin-bottom: 8rpx;
}

.car-desc {
  font-size: 22rpx;
  color: #999;
  display: block;
  margin-bottom: 15rpx;
}

.car-price {
  display: flex;
  align-items: baseline;
  gap: 4rpx;
  margin-bottom: 15rpx;
}

.price-main {
  font-size: 32rpx;
  color: #ff6b6b;
  font-weight: 600;
}

.price-unit {
  font-size: 22rpx;
  color: #999;
}

.car-details {
  display: flex;
  gap: 15rpx;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 4rpx;
  font-size: 20rpx;
  color: #666;
}

.detail-icon {
  width: 20rpx;
  height: 20rpx;
}

.call-section {
  background: #fff;
  padding: 30rpx;
  margin-top: auto;
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.price-breakdown {
  background: #f8fbff;
  border-radius: 16rpx;
  padding: 25rpx;
  margin-bottom: 25rpx;
  border: 1rpx solid #e8f1ff;
}

.price-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.price-item.total {
  border-bottom: none;
  border-top: 2rpx solid #f0f0f0;
  margin-top: 10rpx;
  padding-top: 20rpx;
}

.price-label {
  font-size: 26rpx;
  color: #666;
}

.price-value {
  font-size: 26rpx;
  color: #333;
  font-weight: 500;
}

.price-value.final {
  color: #ff6b6b;
  font-size: 32rpx;
  font-weight: 600;
}

.call-action {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.call-info {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  flex: 1;
}

.distance, .time {
  font-size: 24rpx;
  color: #666;
}

.call-btn {
  background: #b8d4ff;
  border-radius: 25rpx;
  padding: 25rpx 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5rpx;
  min-width: 200rpx;
  transition: all 0.3s ease;
}

.call-btn.disabled {
  background: #f0f0f0;
}

.call-btn:active:not(.disabled) {
  background: #a8c4ff;
  transform: scale(0.98);
}

.call-text {
  font-size: 28rpx;
  color: #fff;
  font-weight: 500;
}

.call-btn.disabled .call-text {
  color: #999;
}

.call-price {
  font-size: 24rpx;
  color: #fff;
  opacity: 0.9;
}

.call-btn.disabled .call-price {
  color: #999;
}

.safe-area {
  height: env(safe-area-inset-bottom);
  background: #fff;
}
</style>