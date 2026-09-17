<template>
  <view class="search-container" :style="{ backgroundColor: bgcolor }">
    <view class="search-box" :style="{ borderRadius: radius + 'px' }">
      <uni-icons type="search" size="18" color="#999"></uni-icons>
      <input 
        class="search-input" 
        :placeholder="placeholder" 
        :focus="autoFocus"
        @confirm="onSearch"
        v-model="searchValue"
      />
    </view>
  </view>
</template>

<script>
export default {
  name: "SearchBar",
  props: {
    bgcolor: {
      type: String,
      default: '#FFFFFF'
    },
    radius: {
      type: Number,
      default: 20
    },
    placeholder: {
      type: String,
      default: '搜索目的地、攻略或景点'
    },
    autoFocus: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      searchValue: ''
    };
  },
  methods: {
    onSearch() {
      this.$emit('search', this.searchValue);
    }
  }
}
</script>

<style scoped>
.search-container {
  padding: 15rpx 30rpx;
  background-color: #FFFFFF;
}
.search-box {
  display: flex;
  align-items: center;
  padding: 10rpx 30rpx;
  background-color: #F5F5F5;
  border-radius: 20px;
}
.search-input {
  flex: 1;
  margin-left: 20rpx;
  font-size: 28rpx;
  background-color: transparent;
}
</style>