<template>
  <view class="hotel-page">
    <!-- 搜索栏 -->
    <view class="search-section">
      <view class="search-bar">
        <image class="search-icon" src="/static/icons/general/search.png" mode="aspectFit"></image>
        <input 
          class="search-input" 
          placeholder="搜索酒店名称、地址" 
          v-model="searchKeyword"
          @input="onSearchInput"
        />
        <view class="search-cancel" @tap="onSearchCancel" v-if="searchKeyword">
          <image class="cancel-icon" src="/static/icons/general/close.png" mode="aspectFit"></image>
        </view>
      </view>
    </view>

    <!-- 日期选择区域 - 直接使用 picker 组件 -->
    <view class="date-section">
      <picker mode="date" :value="checkInDateStr" @change="onCheckInChange">
        <view class="date-item">
          <text class="date-label">入住</text>
          <text class="date-value">{{ checkInDisplayText }}</text>
        </view>
      </picker>
      <view class="date-divider">
        <text>至</text>
      </view>
      <picker mode="date" :value="checkOutDateStr" @change="onCheckOutChange">
        <view class="date-item">
          <text class="date-label">离店</text>
          <text class="date-value">{{ checkOutDisplayText }}</text>
        </view>
      </picker>
      <view class="nights">
        <text>{{ nights }}晚</text>
      </view>
    </view>

    <!-- 筛选条件 -->
    <view class="filter-section">
      <scroll-view class="filter-scroll" scroll-x :show-scrollbar="false">
        <view 
          class="filter-item" 
          v-for="filter in priceFilters" 
          :key="filter.type"
          :class="{ active: priceFilter === filter.type }"
          @tap="onPriceFilterChange(filter.type)"
        >
          <text>{{ filter.name }}</text>
        </view>
      </scroll-view>
    </view>

    <!-- 排序选项 -->
    <view class="sort-section">
      <view 
        class="sort-item" 
        v-for="sort in sortOptions" 
        :key="sort.type"
        :class="{ active: sortType === sort.type }"
        @tap="onSortChange(sort.type)"
      >
        <text>{{ sort.name }}</text>
      </view>
    </view>

    <!-- 酒店列表 -->
    <view class="hotel-list">
      <scroll-view 
        class="list-scroll" 
        scroll-y 
        @scrolltolower="loadMore"
        :refresher-enabled="true"
        :refresher-triggered="refreshing"
        @refresherrefresh="onRefresh"
      >
        <view v-if="loading && allHotels.length === 0" class="loading-container">
          <text class="loading-text">正在获取附近酒店...</text>
        </view>

        <view v-else-if="filteredHotels.length === 0 && !loading" class="empty-container">
          <image class="empty-icon" src="/static/icons/general/empty.png" mode="aspectFit"></image>
          <text class="empty-text">没有找到酒店</text>
          <text class="empty-sub">尝试切换筛选条件或搜索关键词</text>
        </view>

        <view 
          class="hotel-item" 
          v-for="hotel in filteredHotels" 
          :key="hotel.id"
          @tap="viewHotelDetail(hotel)"
        >
          <view class="hotel-info">
            <view class="hotel-header">
              <text class="hotel-name">{{ hotel.name }}</text>
              <view class="hotel-rating">
                <image class="star-icon" src="/static/icons/general/star.png" mode="aspectFit"></image>
                <text>{{ hotel.rating }}</text>
              </view>
            </view>
            
            <view class="hotel-location">
              <image class="location-icon" src="/static/icons/general/location.png" mode="aspectFit"></image>
              <text class="location-text">{{ hotel.location }}</text>
            </view>
            
            <view class="hotel-tags">
              <text class="hotel-tag" v-for="tag in hotel.tags.slice(0, 3)" :key="tag">{{ tag }}</text>
            </view>
            
            <view class="hotel-price">
              <text class="price-from" v-if="hotel.minPrice">¥{{ hotel.minPrice }}起</text>
              <text class="price-from" v-else>暂无报价</text>
              <text class="price-original" v-if="hotel.originalPrice">¥{{ hotel.originalPrice }}</text>
            </view>
            
            <view class="hotel-discount" v-if="hotel.discount">
              <text>{{ hotel.discount }}</text>
            </view>
          </view>
        </view>

        <view class="load-more" v-if="hasMore && allHotels.length > 0">
          <text>{{ loadingMore ? '加载中...' : '加载更多' }}</text>
        </view>
        <view class="load-more" v-else-if="!hasMore && allHotels.length > 0">
          <text>已加载全部酒店</text>
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
          <text class="permission-text">为了提供精准的附近酒店服务，需要获取您的位置信息</text>
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
const TENCENT_MAP_KEY = '4DYBZ-7QXEC-CWM2S-AXAZR-YLVQF-C6BPY';
const TENCENT_MAP_BASE_URL = 'https://apis.map.qq.com';

export default {
  data() {
    return {
      searchKeyword: '',
      // 日期相关数据
      checkInDate: null,      // 入住日期 Date对象
      checkOutDate: null,     // 离店日期 Date对象
      checkInDateStr: '',     // 入住日期字符串 yyyy-mm-dd
      checkOutDateStr: '',    // 离店日期字符串 yyyy-mm-dd
      checkInDisplayText: '', // 入住显示文本
      checkOutDisplayText: '',// 离店显示文本
      nights: 1,              // 住宿晚数
      
      priceFilter: 'all',
      sortType: 'recommend',
      priceFilters: [
        { type: 'all', name: '全部' },
        { type: '0-300', name: '¥0-300' },
        { type: '300-500', name: '¥300-500' },
        { type: '500-800', name: '¥500-800' },
        { type: '800+', name: '¥800以上' }
      ],
      sortOptions: [
        { type: 'recommend', name: '推荐' },
        { type: 'price', name: '价格' },
        { type: 'distance', name: '距离' },
        { type: 'rating', name: '评分' }
      ],
      
      allHotels: [],
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
      
      showPermissionModal: false,
      searchTimer: null
    }
  },
  computed: {
    filteredHotels() {
      let hotels = [...this.allHotels];
      
      if (this.priceFilter !== 'all') {
        hotels = hotels.filter(hotel => {
          const price = hotel.minPrice;
          if (!price) return false;
          switch (this.priceFilter) {
            case '0-300': return price <= 300;
            case '300-500': return price > 300 && price <= 500;
            case '500-800': return price > 500 && price <= 800;
            case '800+': return price > 800;
            default: return true;
          }
        });
      }
      
      switch (this.sortType) {
        case 'price':
          hotels = hotels.sort((a, b) => (a.minPrice || Infinity) - (b.minPrice || Infinity));
          break;
        case 'distance':
          hotels = hotels.sort((a, b) => (a.distanceValue || 0) - (b.distanceValue || 0));
          break;
        case 'rating':
          hotels = hotels.sort((a, b) => (b.rating || 0) - (a.rating || 0));
          break;
        default:
          hotels = hotels.sort((a, b) => {
            const scoreA = (a.distanceValue || 0) / 1000 - (a.rating || 0) * 0.2;
            const scoreB = (b.distanceValue || 0) / 1000 - (b.rating || 0) * 0.2;
            return scoreA - scoreB;
          });
      }
      
      return hotels;
    }
  },
  onLoad() {
    this.initDefaultDates();
    this.getUserLocationAndLoadHotels();
  },
  methods: {
    // 初始化默认日期（今天入住，明天离店）
    initDefaultDates() {
      const today = new Date();
      const tomorrow = new Date(today);
      tomorrow.setDate(tomorrow.getDate() + 1);
      
      this.checkInDate = today;
      this.checkOutDate = tomorrow;
      this.updateDateStringsAndDisplay();
    },
    
    // 更新日期字符串和显示文本
    updateDateStringsAndDisplay() {
      if (this.checkInDate) {
        this.checkInDateStr = this.formatDateYMD(this.checkInDate);
        this.checkInDisplayText = this.getDateDisplayText(this.checkInDate);
      }
      if (this.checkOutDate) {
        this.checkOutDateStr = this.formatDateYMD(this.checkOutDate);
        this.checkOutDisplayText = this.getDateDisplayText(this.checkOutDate);
      }
      this.calculateNights();
    },
    
    // 获取日期显示文本（今天/明天/月日）
    getDateDisplayText(date) {
      if (!date) return '请选择';
      const today = new Date();
      const tomorrow = new Date(today);
      tomorrow.setDate(tomorrow.getDate() + 1);
      
      if (this.isSameDay(date, today)) {
        return '今天';
      } else if (this.isSameDay(date, tomorrow)) {
        return '明天';
      } else {
        const month = date.getMonth() + 1;
        const day = date.getDate();
        return `${month}月${day}日`;
      }
    },
    
    // 判断是否为同一天
    isSameDay(date1, date2) {
      return date1.getFullYear() === date2.getFullYear() &&
             date1.getMonth() === date2.getMonth() &&
             date1.getDate() === date2.getDate();
    },
    
    // 计算住宿晚数
    calculateNights() {
      if (this.checkInDate && this.checkOutDate) {
        const diffTime = Math.abs(this.checkOutDate - this.checkInDate);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        this.nights = diffDays > 0 ? diffDays : 1;
      } else {
        this.nights = 1;
      }
    },
    
    // 格式化日期为 yyyy-mm-dd
    formatDateYMD(date) {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    
    // 解析 yyyy-mm-dd 为 Date 对象
    parseYMDToDate(ymd) {
      const [year, month, day] = ymd.split('-');
      return new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
    },
    
    // 入住日期变更
    onCheckInChange(e) {
      const dateStr = e.detail.value;
      if (!dateStr) return;
      let newCheckIn = this.parseYMDToDate(dateStr);
      let newCheckOut = this.checkOutDate;
      // 如果选择的入住日期 >= 离店日期，自动将离店日期设为入住日期的后一天
      if (newCheckOut && newCheckIn >= newCheckOut) {
        newCheckOut = new Date(newCheckIn);
        newCheckOut.setDate(newCheckOut.getDate() + 1);
        this.checkOutDate = newCheckOut;
      }
      this.checkInDate = newCheckIn;
      this.updateDateStringsAndDisplay();
      // 日期变化后重新加载酒店数据
      this.resetAndLoad();
    },
    
    // 离店日期变更
    onCheckOutChange(e) {
      const dateStr = e.detail.value;
      if (!dateStr) return;
      let newCheckOut = this.parseYMDToDate(dateStr);
      let newCheckIn = this.checkInDate;
      // 如果离店日期 <= 入住日期，自动将离店日期设为入住日期的后一天
      if (newCheckOut <= newCheckIn) {
        newCheckOut = new Date(newCheckIn);
        newCheckOut.setDate(newCheckOut.getDate() + 1);
        uni.showToast({
          title: '离店日期已自动调整',
          icon: 'none',
          duration: 1500
        });
      }
      this.checkOutDate = newCheckOut;
      this.updateDateStringsAndDisplay();
      this.resetAndLoad();
    },
    
    getUserLocationAndLoadHotels() {
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
      this.allHotels = [];
      this.currentPage = 1;
      this.hasMore = true;
      this.loadHotels(true);
    },
    
    async loadHotels(reset = false) {
      if (!this.currentLocation.latitude || !this.currentLocation.longitude) {
        console.warn('位置未获取');
        return;
      }
      
      if (reset) {
        this.currentPage = 1;
        this.hasMore = true;
        this.loading = true;
        this.allHotels = [];
      } else {
        if (this.loadingMore || !this.hasMore) return;
        this.loadingMore = true;
      }
      
      const keyword = this.searchKeyword && this.searchKeyword.trim() ? this.searchKeyword.trim() : '酒店';
      const params = {
        key: TENCENT_MAP_KEY,
        boundary: `nearby(${this.currentLocation.latitude},${this.currentLocation.longitude},5000)`,
        keyword: keyword,
        page_size: this.pageSize,
        page_index: this.currentPage,
        order_by: '_distance'
      };
      
      // 如果需要传递日期参数给后端，可以在这里添加
      // if (this.checkInDate && this.checkOutDate) {
      //   params.check_in = this.checkInDateStr;
      //   params.check_out = this.checkOutDateStr;
      // }
      
      try {
        const res = await this.requestAPI(`${TENCENT_MAP_BASE_URL}/ws/place/v1/search`, params);
        if (res.status === 0 && res.data && res.data.length) {
          let hotelPOIs = res.data.filter(poi => this.isHotelPoi(poi));
          const newHotels = this.parseHotelsFromAPI(hotelPOIs);
          if (reset) {
            this.allHotels = newHotels;
          } else {
            this.allHotels = [...this.allHotels, ...newHotels];
          }
          
          if (res.data.length < this.pageSize) {
            this.hasMore = false;
          } else {
            const total = res.count || 0;
            const loadedCount = this.currentPage * this.pageSize;
            this.hasMore = loadedCount < total;
            if (this.hasMore) this.currentPage++;
          }
        } else {
          if (this.currentPage === 1) {
            uni.showToast({
              title: '未找到附近酒店',
              icon: 'none'
            });
          }
          this.hasMore = false;
        }
      } catch (error) {
        console.error('请求酒店数据失败:', error);
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
    
    isHotelPoi(poi) {
      const category = (poi.category || '').toLowerCase();
      const type = (poi.type || '').toLowerCase();
      const title = (poi.title || '').toLowerCase();
      const hotelKeywords = ['酒店', '宾馆', '旅馆', '住宿', '青年旅舍', '公寓', '度假村', '山庄', '客栈', '民宿', '招待所', '饭店', '大酒店'];
      const excludeKeywords = ['餐厅', '美食', '景点', '公园', '购物', '超市', '银行', '医院', '学校'];
      
      for (let kw of excludeKeywords) {
        if (category.includes(kw) || title.includes(kw)) return false;
      }
      for (let kw of hotelKeywords) {
        if (category.includes(kw) || type.includes(kw) || title.includes(kw)) return true;
      }
      return false;
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
    
    parseHotelsFromAPI(data) {
      return data.map((poi, index) => {
        const id = poi.id || `temp_${Date.now()}_${index}`;
        const name = poi.title || '酒店';
        const address = poi.address || poi.location?.address || '地址待补充';
        
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
        
        let rating = 4.0;
        if (poi.star_level) {
          rating = Math.min(5, Math.max(0, poi.star_level));
        } else if (poi.rate) {
          rating = parseFloat(poi.rate) || 4.0;
        } else {
          rating = 3.5 + (parseInt(id, 36) % 15) / 10;
          rating = Math.min(5, Math.max(3, rating));
        }
        rating = Math.round(rating * 10) / 10;
        
        let minPrice = null;
        if (poi.price && typeof poi.price === 'number') {
          minPrice = poi.price;
        } else if (poi.avg_price) {
          minPrice = poi.avg_price;
        } else {
          minPrice = null;
        }
        
        let tags = [];
        if (poi.category) {
          tags.push(poi.category.split('，')[0]);
        }
        if (rating >= 4.5) tags.push('高评分');
        if (minPrice && minPrice > 500) tags.push('高档型');
        else if (minPrice && minPrice < 200) tags.push('经济实惠');
        if (!tags.length) tags.push('酒店');
        tags.push('免费WiFi');
        if (Math.random() > 0.7) tags.push('含早餐');
        
        let discount = null;
        let originalPrice = null;
        if (minPrice && Math.random() > 0.8) {
          originalPrice = Math.round(minPrice * 1.3);
          discount = '限时优惠';
        }
        
        return {
          id: id,
          name: name,
          rating: rating,
          location: address,
          tags: tags,
          minPrice: minPrice,
          originalPrice: originalPrice,
          discount: discount,
          distance: distance,
          distanceValue: distanceValue,
          latitude: poi.location?.lat || 0,
          longitude: poi.location?.lng || 0
        };
      });
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
    
    onPriceFilterChange(filterType) {
      this.priceFilter = filterType;
    },
    
    onSortChange(sortType) {
      this.sortType = sortType;
    },
    
    viewHotelDetail(hotel) {
      uni.navigateTo({
        url: `/pages/hotel/detail?id=${hotel.id}&name=${encodeURIComponent(hotel.name)}&lat=${hotel.latitude}&lng=${hotel.longitude}`
      });
    },
    
    loadMore() {
      if (!this.hasMore || this.loadingMore || this.loading) return;
      this.loadHotels(false);
    },
    
    onRefresh() {
      this.refreshing = true;
      this.resetAndLoad();
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
              this.getUserLocationAndLoadHotels();
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
.hotel-page {
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
  position: relative;
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

.date-section {
  background: #fff;
  padding: 25rpx 30rpx;
  border-bottom: 1rpx solid #eee;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.date-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
}

.date-item:active {
  opacity: 0.7;
}

.date-label {
  font-size: 24rpx;
  color: #999;
  margin-bottom: 8rpx;
}

.date-value {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
}

.date-divider {
  padding: 0 20rpx;
  color: #999;
}

.nights {
  background: #e8f1ff;
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
  color: #b8d4ff;
  font-size: 24rpx;
}

.filter-section {
  background: #fff;
  padding: 20rpx 30rpx;
  border-bottom: 1rpx solid #eee;
}

.filter-scroll {
  white-space: nowrap;
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

.sort-section {
  background: #fff;
  padding: 20rpx 30rpx;
  border-bottom: 1rpx solid #eee;
  display: flex;
  justify-content: space-around;
}

.sort-item {
  font-size: 26rpx;
  color: #666;
  padding: 10rpx 20rpx;
  transition: all 0.3s ease;
}

.sort-item.active {
  color: #b8d4ff;
  font-weight: 500;
}

.hotel-list {
  flex: 1;
  overflow: hidden;
}

.list-scroll {
  height: 100%;
  padding: 20rpx 30rpx;
}

.hotel-item {
  background: #fff;
  border-radius: 20rpx;
  margin-bottom: 20rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 15rpx rgba(0, 0, 0, 0.06);
}

.hotel-info {
  padding: 25rpx;
  width: 100%;
  box-sizing: border-box;
}

.hotel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15rpx;
}

.hotel-name {
  font-size: 30rpx;
  color: #333;
  font-weight: 600;
  flex: 1;
  margin-right: 15rpx;
}

.hotel-rating {
  display: flex;
  align-items: center;
  gap: 5rpx;
  color: #ffb400;
  font-size: 24rpx;
}

.star-icon {
  width: 24rpx;
  height: 24rpx;
}

.hotel-location {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-bottom: 15rpx;
}

.location-icon {
  width: 20rpx;
  height: 20rpx;
}

.location-text {
  font-size: 24rpx;
  color: #999;
  flex: 1;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.hotel-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  margin-bottom: 20rpx;
}

.hotel-tag {
  font-size: 20rpx;
  color: #b8d4ff;
  background: #f0f7ff;
  padding: 6rpx 12rpx;
  border-radius: 12rpx;
  border: 1rpx solid #e1edff;
}

.hotel-price {
  display: flex;
  align-items: baseline;
  gap: 10rpx;
  margin-bottom: 8rpx;
}

.price-from {
  font-size: 32rpx;
  color: #ff6b6b;
  font-weight: 600;
}

.price-original {
  font-size: 24rpx;
  color: #999;
  text-decoration: line-through;
}

.hotel-discount {
  font-size: 22rpx;
  color: #ff6b6b;
  background: #ffeaea;
  padding: 4rpx 12rpx;
  border-radius: 12rpx;
  align-self: flex-start;
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

.load-more {
  text-align: center;
  padding: 30rpx;
  color: #b8d4ff;
  font-size: 26rpx;
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