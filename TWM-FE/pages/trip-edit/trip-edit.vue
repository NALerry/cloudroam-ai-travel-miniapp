<template>
  <view class="page-container">
    <!-- 页面头部 -->
    <view class="page-header">
      <view class="header-nav">
        <view class="nav-btn" @tap="goBack">
          <image src="/static/icons/general/back.png" class="nav-icon"></image>
        </view>
        <text class="header-title">{{ isEdit ? '编辑行程' : '新建行程' }}</text>
        <view class="nav-btn" @tap="saveTrip">
          <text class="save-text">保存</text>
        </view>
      </view>
    </view>

    <!-- 内容区域 -->
    <scroll-view class="content-scroll" scroll-y :style="{height: scrollHeight + 'px'}">
      <view class="edit-form">
        <!-- 行程名称 -->
        <view class="form-group">
          <text class="form-label">行程名称</text>
          <input 
            class="form-input" 
            v-model="tripForm.name" 
            placeholder="请输入行程名称"
            maxlength="30"
          />
          <text class="input-count">{{ tripForm.name.length }}/30</text>
        </view>

        <!-- 目的地 -->
        <view class="form-group">
          <text class="form-label">目的地</text>
          <input 
            class="form-input" 
            v-model="tripForm.destination" 
            placeholder="请输入目的地"
            maxlength="50"
          />
        </view>

        <!-- 日期范围 -->
        <view class="form-group">
          <text class="form-label">行程日期</text>
          <view class="date-range">
            <picker 
              mode="date" 
              :value="tripForm.startDate" 
              @change="onStartDateChange"
            >
              <view class="date-input">
                <text :class="tripForm.startDate ? 'date-text' : 'date-placeholder'">
                  {{ tripForm.startDate || '开始日期' }}
                </text>
              </view>
            </picker>
            <text class="date-separator">至</text>
            <picker 
              mode="date" 
              :value="tripForm.endDate" 
              @change="onEndDateChange"
            >
              <view class="date-input">
                <text :class="tripForm.endDate ? 'date-text' : 'date-placeholder'">
                  {{ tripForm.endDate || '结束日期' }}
                </text>
              </view>
            </picker>
          </view>
          <text class="date-days" v-if="tripForm.startDate && tripForm.endDate">
            共 {{ calculateDays(tripForm.startDate, tripForm.endDate) }} 天
          </text>
        </view>

        <!-- 行程状态 -->
        <view class="form-group">
          <text class="form-label">行程状态</text>
          <view class="status-options">
            <view 
              class="status-option" 
              :class="{ active: tripForm.status === 'planned' }"
              @tap="tripForm.status = 'planned'"
            >
              <text class="status-text">计划中</text>
            </view>
            <view 
              class="status-option" 
              :class="{ active: tripForm.status === 'ongoing' }"
              @tap="tripForm.status = 'ongoing'"
            >
              <text class="status-text">进行中</text>
            </view>
            <view 
              class="status-option" 
              :class="{ active: tripForm.status === 'completed' }"
              @tap="tripForm.status = 'completed'"
            >
              <text class="status-text">已完成</text>
            </view>
          </view>
        </view>

        <!-- 行程描述 -->
        <view class="form-group">
          <text class="form-label">行程描述</text>
          <textarea 
            class="form-textarea" 
            v-model="tripForm.description" 
            placeholder="描述一下您的旅行计划..."
            maxlength="200"
          ></textarea>
          <text class="input-count">{{ tripForm.description.length }}/200</text>
        </view>

        <!-- 行程预算 -->
        <view class="form-group">
          <text class="form-label">预算（元）</text>
          <input 
            class="form-input" 
            v-model="tripForm.budget" 
            placeholder="请输入预算金额"
            type="number"
          />
        </view>

        <!-- 同行人员 -->
        <view class="form-group">
          <text class="form-label">同行人员</text>
          <view class="companions-input">
            <input 
              class="companion-input" 
              v-model="newCompanion" 
              placeholder="输入同行人员姓名"
              maxlength="10"
              @confirm="addCompanion"
            />
            <view class="companions-list">
              <view 
                class="companion-item" 
                v-for="(companion, index) in tripForm.companions" 
                :key="index"
              >
                <text class="companion-text">{{ companion }}</text>
                <view class="companion-remove" @tap="removeCompanion(index)">
                  <image src="/static/icons/general/close.png" class="remove-icon"></image>
                </view>
              </view>
            </view>
          </view>
        </view>

        <!-- 注意事项 -->
        <view class="form-group">
          <text class="form-label">注意事项</text>
          <textarea 
            class="form-textarea" 
            v-model="tripForm.notes" 
            placeholder="记录重要的注意事项..."
            maxlength="500"
          ></textarea>
          <text class="input-count">{{ tripForm.notes.length }}/500</text>
        </view>
      </view>

      <!-- 删除按钮 -->
      <view class="delete-section" v-if="isEdit">
        <view class="delete-btn" @tap="deleteTrip">
          <text class="delete-text">删除行程</text>
        </view>
      </view>

      <!-- 底部安全区域 -->
      <view class="safe-area"></view>
    </scroll-view>

    <!-- 加载状态 -->
    <view class="loading-mask" v-if="loading">
      <view class="loading-content">
        <image src="/static/icons/general/loading.png" class="loading-icon"></image>
        <text class="loading-text">保存中...</text>
      </view>
    </view>
  </view>
</template>

<script>
import { formatDate } from '@/utils/date.js'

export default {
  data() {
    return {
      tripForm: {
        id: null,
        name: '',
        destination: '',
        startDate: formatDate(new Date()),
        endDate: formatDate(new Date()),
        status: 'planned',
        description: '',
        budget: '',
        companions: [],
        notes: '',
        createTime: ''
      },
      newCompanion: '',
      isEdit: false,
      loading: false,
      scrollHeight: 0
    }
  },
  onLoad(options) {
    this.calculateScrollHeight()
    if (options.id) {
      this.isEdit = true
      this.loadTripData(options.id)
    } else {
      this.tripForm.createTime = new Date().toISOString()
    }
  },
  methods: {
    calculateScrollHeight() {
      const systemInfo = uni.getSystemInfoSync()
      const windowHeight = systemInfo.windowHeight
      const statusBarHeight = systemInfo.statusBarHeight || 0
      const navigationBarHeight = 44
      this.scrollHeight = windowHeight - statusBarHeight - navigationBarHeight
    },
    
    loadTripData(id) {
      try {
        const trips = uni.getStorageSync('user_trips') || []
        const trip = trips.find(t => t.id == id)
        if (trip) {
          this.tripForm = { 
            ...this.tripForm,
            ...trip,
            companions: trip.companions || [],
            notes: trip.notes || '',
            budget: trip.budget || ''
          }
        } else {
          uni.showToast({
            title: '行程不存在',
            icon: 'none'
          })
          setTimeout(() => {
            uni.navigateBack()
          }, 1500)
        }
      } catch (error) {
        console.error('加载行程数据失败:', error)
        uni.showToast({
          title: '加载失败',
          icon: 'none'
        })
      }
    },
    
    goBack() {
      uni.navigateBack()
    },
    
    onStartDateChange(e) {
      this.tripForm.startDate = e.detail.value
      // 如果结束日期早于开始日期，自动调整结束日期
      if (this.tripForm.endDate && new Date(this.tripForm.endDate) < new Date(this.tripForm.startDate)) {
        this.tripForm.endDate = this.tripForm.startDate
      }
    },
    
    onEndDateChange(e) {
      this.tripForm.endDate = e.detail.value
    },
    
    calculateDays(startDate, endDate) {
      if (!startDate || !endDate) return 0
      const start = new Date(startDate)
      const end = new Date(endDate)
      const diffTime = Math.abs(end - start)
      return Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
    },
    
    addCompanion() {
      if (this.newCompanion.trim() && this.tripForm.companions.length < 10) {
        this.tripForm.companions.push(this.newCompanion.trim())
        this.newCompanion = ''
      }
    },
    
    removeCompanion(index) {
      this.tripForm.companions.splice(index, 1)
    },
    
    async saveTrip() {
      if (!this.validateForm()) return
      
      this.loading = true
      try {
        await new Promise(resolve => setTimeout(resolve, 800))
        
        const trips = uni.getStorageSync('user_trips') || []
        
        if (this.isEdit) {
          // 更新现有行程
          const index = trips.findIndex(t => t.id == this.tripForm.id)
          if (index !== -1) {
            trips[index] = { ...this.tripForm }
          }
        } else {
          // 创建新行程
          const newTrip = {
            ...this.tripForm,
            id: Date.now(),
            createTime: new Date().toISOString()
          }
          trips.unshift(newTrip)
        }
        
        uni.setStorageSync('user_trips', trips)
        
        uni.showToast({
          title: '保存成功',
          icon: 'success'
        })
        
        setTimeout(() => {
          uni.navigateBack()
        }, 1500)
        
      } catch (error) {
        console.error('保存行程失败:', error)
        uni.showToast({
          title: '保存失败',
          icon: 'none'
        })
      } finally {
        this.loading = false
      }
    },
    
    validateForm() {
      if (!this.tripForm.name.trim()) {
        uni.showToast({
          title: '请输入行程名称',
          icon: 'none'
        })
        return false
      }
      
      if (!this.tripForm.destination.trim()) {
        uni.showToast({
          title: '请输入目的地',
          icon: 'none'
        })
        return false
      }
      
      if (!this.tripForm.startDate || !this.tripForm.endDate) {
        uni.showToast({
          title: '请选择行程日期',
          icon: 'none'
        })
        return false
      }
      
      if (new Date(this.tripForm.endDate) < new Date(this.tripForm.startDate)) {
        uni.showToast({
          title: '结束日期不能早于开始日期',
          icon: 'none'
        })
        return false
      }
      
      return true
    },
    
    deleteTrip() {
      uni.showModal({
        title: '删除行程',
        content: '确定要删除这个行程吗？此操作不可恢复。',
        confirmColor: '#ff4444',
        success: (res) => {
          if (res.confirm) {
            this.performDeleteTrip()
          }
        }
      })
    },
    
    async performDeleteTrip() {
      this.loading = true
      try {
        await new Promise(resolve => setTimeout(resolve, 500))
        
        const trips = uni.getStorageSync('user_trips') || []
        const filteredTrips = trips.filter(t => t.id != this.tripForm.id)
        uni.setStorageSync('user_trips', filteredTrips)
        
        uni.showToast({
          title: '删除成功',
          icon: 'success'
        })
        
        setTimeout(() => {
          uni.navigateBack()
        }, 1500)
        
      } catch (error) {
        console.error('删除行程失败:', error)
        uni.showToast({
          title: '删除失败',
          icon: 'none'
        })
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: #f8f8f8;
}

/* 页面头部 */
.page-header {
  background: #fff;
  border-bottom: 1rpx solid #f0f0f0;
  padding: 0 30rpx;
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.header-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.nav-btn {
  padding: 16rpx;
}

.nav-icon {
  width: 32rpx;
  height: 32rpx;
}

.header-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.save-text {
  font-size: 32rpx;
  color: #2c6be8;
  font-weight: 500;
}

/* 内容区域 */
.content-scroll {
  background: #f8f8f8;
}

.edit-form {
  background: #fff;
  margin-bottom: 20rpx;
  border-radius: 0;
}

.form-group {
  padding: 30rpx;
  border-bottom: 1rpx solid #f8f8f8;
}

.form-group:last-child {
  border-bottom: none;
}

.form-label {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
  display: block;
  margin-bottom: 20rpx;
}

.form-input {
  font-size: 28rpx;
  color: #333;
  padding: 20rpx 0;
  width: 100%;
}

.input-count {
  font-size: 24rpx;
  color: #999;
  text-align: right;
  display: block;
  margin-top: 16rpx;
}

/* 日期范围 */
.date-range {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.date-input {
  flex: 1;
  padding: 20rpx;
  background: #f8f8f8;
  border-radius: 8rpx;
  text-align: center;
}

.date-text {
  font-size: 28rpx;
  color: #333;
}

.date-placeholder {
  font-size: 28rpx;
  color: #999;
}

.date-separator {
  font-size: 28rpx;
  color: #666;
}

.date-days {
  font-size: 24rpx;
  color: #2c6be8;
  text-align: center;
  display: block;
  margin-top: 16rpx;
}

/* 状态选项 */
.status-options {
  display: flex;
  gap: 20rpx;
}

.status-option {
  flex: 1;
  padding: 20rpx;
  text-align: center;
  background: #f8f8f8;
  border-radius: 8rpx;
  border: 2rpx solid transparent;
}

.status-option.active {
  background: #e8f1ff;
  border-color: #2c6be8;
}

.status-text {
  font-size: 28rpx;
  color: #666;
}

.status-option.active .status-text {
  color: #2c6be8;
  font-weight: 500;
}

.form-textarea {
  font-size: 28rpx;
  color: #333;
  width: 100%;
  height: 160rpx;
  line-height: 1.6;
  background: #f8f8f8;
  border-radius: 8rpx;
  padding: 20rpx;
}

/* 同行人员 */
.companions-input {
  margin-top: 20rpx;
}

.companion-input {
  font-size: 28rpx;
  color: #333;
  padding: 20rpx;
  background: #f8f8f8;
  border-radius: 8rpx;
  margin-bottom: 20rpx;
}

.companions-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.companion-item {
  display: flex;
  align-items: center;
  background: #e8f1ff;
  padding: 12rpx 20rpx;
  border-radius: 20rpx;
}

.companion-text {
  font-size: 24rpx;
  color: #2c6be8;
  margin-right: 8rpx;
}

.companion-remove {
  width: 24rpx;
  height: 24rpx;
  border-radius: 12rpx;
  background: #2c6be8;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-icon {
  width: 12rpx;
  height: 12rpx;
}

/* 删除按钮 */
.delete-section {
  padding: 40rpx 30rpx;
}

.delete-btn {
  background: #fff;
  border-radius: 16rpx;
  padding: 28rpx;
  text-align: center;
  border: 1rpx solid #ff4444;
}

.delete-text {
  font-size: 32rpx;
  color: #ff4444;
  font-weight: 500;
}

/* 加载状态 */
.loading-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-content {
  background: #fff;
  padding: 40rpx;
  border-radius: 16rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.loading-icon {
  width: 60rpx;
  height: 60rpx;
  margin-bottom: 20rpx;
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 28rpx;
  color: #666;
}

/* 安全区域 */
.safe-area {
  height: env(safe-area-inset-bottom);
  background: #f8f8f8;
}
</style>