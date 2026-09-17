<template>
  <view class="homestay-page">
    <!-- 搜索栏 -->
    <view class="search-section">
      <view class="search-bar">
        <image class="search-icon" src="/static/icons/general/search.png" mode="aspectFit"></image>
        <input 
          class="search-input" 
          placeholder="搜索民宿名称、地址" 
          v-model="searchKeyword"
          @input="onSearchInput"
        />
        <view class="search-cancel" @tap="onSearchCancel" v-if="searchKeyword">
          <image class="cancel-icon" src="/static/icons/general/close.png" mode="aspectFit"></image>
        </view>
      </view>
    </view>

    <!-- 日期选择 -->
    <view class="date-section">
      <view class="date-item" @tap="showDatePicker = true">
        <text class="date-label">入住</text>
        <text class="date-value">{{ checkInDate }}</text>
      </view>
      <view class="date-divider"><text>至</text></view>
      <view class="date-item" @tap="showDatePicker = true">
        <text class="date-label">离店</text>
        <text class="date-value">{{ checkOutDate }}</text>
      </view>
      <view class="nights"><text>{{ nights }}晚</text></view>
    </view>

    <!-- 价格筛选 -->
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

    <!-- 排序 -->
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

    <!-- 列表 -->
    <view class="homestay-list">
      <scroll-view 
        class="list-scroll" 
        scroll-y 
        @scrolltolower="loadMore"
        :refresher-enabled="true"
        :refresher-triggered="refreshing"
        @refresherrefresh="onRefresh"
      >
        <view v-if="loading && allHomestays.length === 0" class="loading-container">
          <text class="loading-text">正在获取附近民宿...</text>
        </view>
        <view v-else-if="filteredHomestays.length === 0 && !loading" class="empty-container">
          <image class="empty-icon" src="/static/icons/general/empty.png" mode="aspectFit"></image>
          <text class="empty-text">没有找到民宿</text>
          <text class="empty-sub">尝试切换筛选条件或搜索关键词</text>
        </view>
        <view 
          class="homestay-item" 
          v-for="item in filteredHomestays" 
          :key="item.id"
          @tap="viewDetail(item)"
        >
          <view class="homestay-info">
            <view class="homestay-header">
              <text class="homestay-name">{{ item.name }}</text>
              <view class="homestay-rating">
                <image class="star-icon" src="/static/icons/general/star.png" mode="aspectFit"></image>
                <text>{{ item.rating }}</text>
              </view>
            </view>
            <view class="homestay-location">
              <image class="location-icon" src="/static/icons/general/location.png" mode="aspectFit"></image>
              <text class="location-text">{{ item.location }}</text>
            </view>
            <view class="homestay-tags">
              <text class="homestay-tag" v-for="tag in item.tags.slice(0, 3)" :key="tag">{{ tag }}</text>
            </view>
            <view class="homestay-price">
              <text class="price-from" v-if="item.minPrice">¥{{ item.minPrice }}起</text>
              <text class="price-from" v-else>暂无报价</text>
              <text class="price-original" v-if="item.originalPrice">¥{{ item.originalPrice }}</text>
            </view>
            <view class="homestay-discount" v-if="item.discount"><text>{{ item.discount }}</text></view>
          </view>
        </view>
        <view class="load-more" v-if="hasMore && allHomestays.length > 0">
          <text>{{ loadingMore ? '加载中...' : '加载更多' }}</text>
        </view>
        <view class="load-more" v-else-if="!hasMore && allHomestays.length > 0">
          <text>已加载全部民宿</text>
        </view>
      </scroll-view>
    </view>

    <uni-calendar v-if="showDatePicker" :insert="false" @close="showDatePicker = false" @confirm="onDateConfirm" />
    <view class="safe-area"></view>

    <!-- 定位权限弹窗 -->
    <view class="permission-modal" v-if="showPermissionModal">
      <view class="permission-content">
        <view class="permission-header"><text class="permission-title">位置权限申请</text></view>
        <view class="permission-body"><text class="permission-text">为了提供精准的附近民宿服务，需要获取您的位置信息</text></view>
        <view class="permission-actions">
          <view class="permission-btn cancel" @tap="hidePermissionModal">取消</view>
          <view class="permission-btn confirm" @tap="requestLocationPermission">去设置</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
const TENCENT_MAP_KEY = '4DYBZ-7QXEC-CWM2S-AXAZR-YLVQF-C6BPY';
const TENCENT_MAP_BASE_URL = 'https://apis.map.qq.com';

export default {
  data() {
    return {
      searchKeyword: '',
      checkInDate: '今天',
      checkOutDate: '明天',
      nights: 1,
      priceFilter: 'all',
      sortType: 'recommend',
      showDatePicker: false,
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
      allHomestays: [],
      currentPage: 1,
      pageSize: 20,
      hasMore: true,
      loading: false,
      loadingMore: false,
      refreshing: false,
      currentLocation: { latitude: null, longitude: null },
      showPermissionModal: false,
      searchTimer: null
    }
  },
  computed: {
    filteredHomestays() {
      let items = [...this.allHomestays];
      if (this.priceFilter !== 'all') {
        items = items.filter(item => {
          const price = item.minPrice;
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
        case 'price': items.sort((a,b) => (a.minPrice||Infinity) - (b.minPrice||Infinity)); break;
        case 'distance': items.sort((a,b) => (a.distanceValue||0) - (b.distanceValue||0)); break;
        case 'rating': items.sort((a,b) => (b.rating||0) - (a.rating||0)); break;
        default: items.sort((a,b) => (a.distanceValue/1000 - a.rating*0.2) - (b.distanceValue/1000 - b.rating*0.2));
      }
      return items;
    }
  },
  onLoad() {
    this.getUserLocationAndLoadHomestays();
  },
  methods: {
    getUserLocationAndLoadHomestays() {
      this.loading = true;
      uni.getLocation({
        type: 'gcj02',
        success: (res) => {
          this.currentLocation.latitude = res.latitude;
          this.currentLocation.longitude = res.longitude;
          this.resetAndLoad();
        },
        fail: () => this.tryTencentIPLocation()
      });
    },
    async tryTencentIPLocation() {
      try {
        const res = await uni.request({ url: `${TENCENT_MAP_BASE_URL}/ws/location/v1/ip?key=${TENCENT_MAP_KEY}&output=json` });
        if (res[1]?.data?.status === 0 && res[1].data.result?.location) {
          const loc = res[1].data.result.location;
          this.currentLocation.latitude = loc.lat;
          this.currentLocation.longitude = loc.lng;
          uni.showToast({ title: '使用IP定位', icon: 'none', duration: 1500 });
          this.resetAndLoad();
        } else throw new Error('IP定位失败');
      } catch(e) {
        this.loading = false;
        this.showPermissionModal = true;
      }
    },
    resetAndLoad() {
      this.allHomestays = [];
      this.currentPage = 1;
      this.hasMore = true;
      this.loadHomestays(true);
    },
    async loadHomestays(reset = false) {
      if (!this.currentLocation.latitude || !this.currentLocation.longitude) return;
      if (reset) {
        this.currentPage = 1;
        this.hasMore = true;
        this.loading = true;
        this.allHomestays = [];
      } else {
        if (this.loadingMore || !this.hasMore) return;
        this.loadingMore = true;
      }
      // 搜索关键词：用户输入或默认“民宿”
      const keyword = this.searchKeyword.trim() || '民宿';
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
        if (res.status === 0 && res.data?.length) {
          // 过滤出民宿类POI
          let homestayPOIs = res.data.filter(poi => this.isHomestayPoi(poi));
          const newItems = this.parseHomestaysFromAPI(homestayPOIs);
          if (reset) this.allHomestays = newItems;
          else this.allHomestays.push(...newItems);
          if (res.data.length < this.pageSize) this.hasMore = false;
          else {
            const total = res.count || 0;
            const loadedCount = this.currentPage * this.pageSize;
            this.hasMore = loadedCount < total;
            if (this.hasMore) this.currentPage++;
          }
        } else {
          if (this.currentPage === 1) uni.showToast({ title: '未找到附近民宿', icon: 'none' });
          this.hasMore = false;
        }
      } catch(e) {
        uni.showToast({ title: '网络错误', icon: 'none' });
      } finally {
        this.loading = false;
        this.loadingMore = false;
        this.refreshing = false;
      }
    },
    isHomestayPoi(poi) {
      const category = (poi.category || '').toLowerCase();
      const title = (poi.title || '').toLowerCase();
      const homestayKeywords = ['民宿','客栈','公寓','度假村','山庄','青年旅舍'];
      const exclude = ['餐厅','美食','景点','公园','购物','超市','银行','医院','学校'];
      for (let kw of exclude) if (category.includes(kw) || title.includes(kw)) return false;
      for (let kw of homestayKeywords) if (category.includes(kw) || title.includes(kw)) return true;
      // 如果标题明确包含“民宿”则特别保留
      if (title.includes('民宿')) return true;
      return false;
    },
    requestAPI(url, params) {
      return new Promise((resolve, reject) => {
        uni.request({ url, data: params, success: res => {
          if (res.statusCode === 200 && res.data.status === 0) resolve(res.data);
          else reject(res.data);
        }, fail: reject });
      });
    },
    parseHomestaysFromAPI(data) {
      return data.map((poi, idx) => {
        const id = poi.id || `tmp_${Date.now()}_${idx}`;
        const name = poi.title || '民宿';
        const address = poi.address || '地址待补充';
        let distance = '', distanceValue = 0;
        if (poi._distance) {
          distanceValue = poi._distance;
          distance = poi._distance < 1000 ? `${Math.round(poi._distance)}m` : `${(poi._distance/1000).toFixed(1)}km`;
        } else distance = '未知距离';
        let rating = 4.0;
        if (poi.star_level) rating = Math.min(5, Math.max(0, poi.star_level));
        else if (poi.rate) rating = parseFloat(poi.rate) || 4.0;
        else rating = 3.5 + (parseInt(id,36)%15)/10;
        rating = Math.round(rating*10)/10;
        let minPrice = poi.price || poi.avg_price || null;
        let tags = [];
        if (poi.category) tags.push(poi.category.split('，')[0]);
        if (rating >= 4.5) tags.push('高评分');
        if (minPrice && minPrice > 400) tags.push('高档民宿');
        else if (minPrice && minPrice < 150) tags.push('经济民宿');
        if (!tags.length) tags.push('民宿');
        tags.push('WiFi');
        let discount = null, originalPrice = null;
        if (minPrice && Math.random() > 0.8) {
          originalPrice = Math.round(minPrice * 1.2);
          discount = '限时优惠';
        }
        return { id, name, rating, location: address, tags, minPrice, originalPrice, discount, distance, distanceValue, latitude: poi.location?.lat||0, longitude: poi.location?.lng||0 };
      });
    },
    onSearchInput() { clearTimeout(this.searchTimer); this.searchTimer = setTimeout(() => this.resetAndLoad(), 500); },
    onSearchCancel() { this.searchKeyword = ''; this.resetAndLoad(); },
    onPriceFilterChange(type) { this.priceFilter = type; },
    onSortChange(type) { this.sortType = type; },
    onDateConfirm(e) { this.showDatePicker = false; },
    viewDetail(item) { uni.navigateTo({ url: `/pages/homestay/detail?id=${item.id}&name=${encodeURIComponent(item.name)}&lat=${item.latitude}&lng=${item.longitude}` }); },
    loadMore() { if (!this.hasMore || this.loadingMore || this.loading) return; this.loadHomestays(false); },
    onRefresh() { this.refreshing = true; this.resetAndLoad(); },
    hidePermissionModal() { this.showPermissionModal = false; },
    requestLocationPermission() {
      this.hidePermissionModal();
      uni.openSetting({
        success(res) { if (res.authSetting['scope.userLocation']) setTimeout(() => this.getUserLocationAndLoadHomestays(), 1000); },
        fail() { uni.showToast({ title: '打开设置失败', icon: 'none' }); }
      });
    }
  }
}
</script>

<style scoped>
.homestay-page { height: 100vh; background: #f8f8f8; display: flex; flex-direction: column; }
.search-section { background: #fff; padding: 20rpx 30rpx; border-bottom: 1rpx solid #eee; }
.search-bar { display: flex; align-items: center; background: #f5f5f5; border-radius: 25rpx; padding: 15rpx 20rpx; }
.search-icon { width: 28rpx; height: 28rpx; margin-right: 15rpx; }
.search-input { flex: 1; font-size: 28rpx; }
.search-cancel { width: 32rpx; height: 32rpx; display: flex; align-items: center; justify-content: center; }
.cancel-icon { width: 20rpx; height: 20rpx; }
.date-section { background: #fff; padding: 25rpx 30rpx; border-bottom: 1rpx solid #eee; display: flex; align-items: center; justify-content: space-between; }
.date-item { flex: 1; display: flex; flex-direction: column; align-items: center; }
.date-label { font-size: 24rpx; color: #999; margin-bottom: 8rpx; }
.date-value { font-size: 28rpx; color: #333; font-weight: 500; }
.nights { background: #e8f1ff; padding: 8rpx 16rpx; border-radius: 20rpx; color: #b8d4ff; font-size: 24rpx; }
.filter-section { background: #fff; padding: 20rpx 30rpx; border-bottom: 1rpx solid #eee; }
.filter-scroll { white-space: nowrap; }
.filter-item { display: inline-flex; padding: 12rpx 24rpx; background: #f5f5f5; border-radius: 25rpx; margin-right: 20rpx; font-size: 24rpx; color: #666; }
.filter-item.active { background: #b8d4ff; color: #fff; }
.sort-section { background: #fff; padding: 20rpx 30rpx; border-bottom: 1rpx solid #eee; display: flex; justify-content: space-around; }
.sort-item { font-size: 26rpx; color: #666; padding: 10rpx 20rpx; }
.sort-item.active { color: #b8d4ff; font-weight: 500; }
.homestay-list { flex: 1; overflow: hidden; }
.list-scroll { height: 100%; padding: 20rpx 30rpx; }
.homestay-item { background: #fff; border-radius: 20rpx; margin-bottom: 20rpx; box-shadow: 0 4rpx 15rpx rgba(0,0,0,0.06); }
.homestay-info { padding: 25rpx; }
.homestay-header { display: flex; justify-content: space-between; margin-bottom: 15rpx; }
.homestay-name { font-size: 30rpx; font-weight: 600; color: #333; flex:1; margin-right:15rpx; }
.homestay-rating { display: flex; align-items: center; gap:5rpx; color:#ffb400; font-size:24rpx; }
.star-icon { width:24rpx; height:24rpx; }
.homestay-location { display:flex; align-items:center; gap:8rpx; margin-bottom:15rpx; }
.location-icon { width:20rpx; height:20rpx; }
.location-text { font-size:24rpx; color:#999; flex:1; overflow:hidden; white-space:nowrap; text-overflow:ellipsis; }
.homestay-tags { display:flex; flex-wrap:wrap; gap:10rpx; margin-bottom:20rpx; }
.homestay-tag { font-size:20rpx; color:#b8d4ff; background:#f0f7ff; padding:6rpx 12rpx; border-radius:12rpx; border:1rpx solid #e1edff; }
.homestay-price { display:flex; align-items:baseline; gap:10rpx; margin-bottom:8rpx; }
.price-from { font-size:32rpx; color:#ff6b6b; font-weight:600; }
.price-original { font-size:24rpx; color:#999; text-decoration:line-through; }
.homestay-discount { font-size:22rpx; color:#ff6b6b; background:#ffeaea; padding:4rpx 12rpx; border-radius:12rpx; align-self:flex-start; }
.load-more { text-align:center; padding:30rpx; color:#b8d4ff; font-size:26rpx; }
.loading-container, .empty-container { display:flex; flex-direction:column; align-items:center; padding:100rpx 0; }
.empty-icon { width:120rpx; height:120rpx; opacity:0.5; margin-bottom:20rpx; }
.empty-text { font-size:28rpx; color:#999; }
.empty-sub { font-size:24rpx; color:#ccc; margin-top:10rpx; }
.safe-area { height: env(safe-area-inset-bottom); }
.permission-modal { position:fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.5); display:flex; align-items:center; justify-content:center; z-index:1000; }
.permission-content { background:#fff; border-radius:20rpx; width:600rpx; overflow:hidden; }
.permission-header { padding:40rpx 30rpx 20rpx; text-align:center; }
.permission-title { font-size:32rpx; font-weight:600; }
.permission-body { padding:0 30rpx 40rpx; text-align:center; }
.permission-text { font-size:28rpx; color:#666; line-height:1.5; }
.permission-actions { display:flex; border-top:1rpx solid #eee; }
.permission-btn { flex:1; text-align:center; padding:30rpx; font-size:28rpx; }
.permission-btn.cancel { color:#999; border-right:1rpx solid #eee; }
.permission-btn.confirm { color:#b8d4ff; font-weight:500; }
</style>