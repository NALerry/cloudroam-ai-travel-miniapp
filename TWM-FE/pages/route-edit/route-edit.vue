<template>
  <view class="page-container">
    <!-- 页面头部 -->
    <view class="page-header">
      <view class="header-content">
        <view class="header-back" @tap="goBack">
          <image src="/static/icons/general/back.png" class="back-icon" mode="aspectFit"></image>
        </view>
        <text class="header-title">{{ isEdit ? '编辑路线' : '创建路线' }}</text>
        <view class="header-actions">
          <!-- 已删除保存按钮 -->
        </view>
      </view>
      <view class="header-bg"></view>
    </view>

    <!-- 内容区域 -->
    <scroll-view class="content-scroll" scroll-y :style="{height: scrollHeight + 'px'}">
      <!-- 基本信息 -->
      <view class="form-section">
        <view class="section-title">
          <image src="/static/icons/general/bill.png" class="section-icon" mode="aspectFit"></image>
          <text class="section-title-text">基本信息</text>
        </view>

        <view class="form-card">
          <!-- 路线名称 -->
          <view class="form-item">
            <text class="form-label">路线名称</text>
            <input 
              class="form-input" 
              v-model="formData.name" 
              placeholder="请输入路线名称"
              placeholder-class="placeholder"
              maxlength="20"
              @focus="onInputFocus"
              @blur="onInputBlur"
            />
            <text class="char-count">{{ formData.name.length }}/20</text>
          </view>

          <!-- 路线描述 -->
          <view class="form-item">
            <text class="form-label">路线描述</text>
            <textarea 
              class="form-textarea" 
              v-model="formData.description" 
              placeholder="请输入路线描述"
              placeholder-class="placeholder"
              maxlength="200"
              @focus="onInputFocus"
              @blur="onInputBlur"
            />
            <text class="char-count">{{ formData.description.length }}/200</text>
          </view>

          <!-- 行程天数 -->
          <view class="form-item">
            <text class="form-label">行程天数</text>
            <view class="number-input">
              <view class="number-btn" @tap="decreaseDuration">-</view>
              <text class="number-value">{{ formData.duration }}天</text>
              <view class="number-btn" @tap="increaseDuration">+</view>
            </view>
          </view>

          <!-- 总里程 -->
          <view class="form-item">
            <text class="form-label">总里程(km)</text>
            <input 
              class="form-input" 
              v-model="formData.distance" 
              type="digit"
              placeholder="请输入总里程"
              placeholder-class="placeholder"
              @focus="onInputFocus"
              @blur="onInputBlur"
            />
          </view>
        </view>
      </view>

      <!-- 地点安排 -->
      <view class="form-section">
        <view class="section-title">
          <image src="/static/icons/general/gps.png" class="section-icon" mode="aspectFit"></image>
          <text class="section-title-text">地点安排</text>
          <text class="section-subtitle">按顺序添加途经地点</text>
        </view>

        <view class="form-card">
          <!-- 地点列表 -->
          <view class="places-list">
            <view 
              class="place-item" 
              v-for="(place, index) in formData.places" 
              :key="index"
            >
              <view class="place-order">
                <text class="order-text">第{{ index + 1 }}站</text>
              </view>
              <input 
                class="place-input" 
                v-model="formData.places[index]" 
                :placeholder="`请输入第${index + 1}个地点`"
                placeholder-class="placeholder"
                @focus="onInputFocus"
                @blur="onInputBlur"
              />
              <view class="place-actions">
                <view class="action-btn up" @tap.stop="movePlaceUp(index)" v-if="index > 0">
                  <image src="/static/icons/general/up.png" class="action-icon" mode="aspectFit"></image>
                </view>
                <view class="action-btn down" @tap.stop="movePlaceDown(index)" v-if="index < formData.places.length - 1">
                  <image src="/static/icons/general/down.png" class="action-icon" mode="aspectFit"></image>
                </view>
                <view class="action-btn delete" @tap.stop="removePlace(index)" v-if="formData.places.length > 1">
                  <image src="/static/icons/general/delete.png" class="action-icon" mode="aspectFit"></image>
                </view>
              </view>
            </view>
          </view>

          <!-- 添加地点按钮 -->
          <view class="add-place-btn" @tap="addPlace" v-if="formData.places.length < 10">
            <image src="/static/icons/general/add.png" class="add-icon" mode="aspectFit"></image>
            <text class="add-text">添加地点</text>
          </view>
          <view class="place-limit-tip" v-else>
            <text class="limit-text">最多添加10个地点</text>
          </view>
        </view>
      </view>

      <!-- 标签分类 -->
      <view class="form-section">
        <view class="section-title">
          <image src="/static/icons/general/tag.png" class="section-icon" mode="aspectFit"></image>
          <text class="section-title-text">标签分类</text>
          <text class="section-subtitle">为路线添加标签，便于分类</text>
        </view>

        <view class="form-card">
          <!-- 标签输入 -->
          <view class="tag-input-container">
            <input 
              class="tag-input" 
              v-model="newTag" 
              placeholder="输入标签后按回车添加"
              placeholder-class="placeholder"
              maxlength="6"
              @confirm="addTag"
              @focus="onInputFocus"
              @blur="onInputBlur"
            />
            <view class="add-tag-btn" @tap="addTag">
              <text class="add-tag-text">添加</text>
            </view>
          </view>

          <!-- 标签列表 -->
          <view class="tags-list">
            <view 
              class="tag-item" 
              v-for="(tag, index) in formData.tags" 
              :key="index"
            >
              <text class="tag-text">{{ tag }}</text>
              <view class="tag-remove" @tap="removeTag(index)">
                <image src="/static/icons/general/close.png" class="remove-icon" mode="aspectFit"></image>
              </view>
            </view>
            <view class="no-tags" v-if="formData.tags.length === 0">
              <text class="no-tags-text">暂无标签</text>
            </view>
          </view>

          <!-- 推荐标签 -->
          <view class="recommended-tags">
            <text class="recommend-title">推荐标签：</text>
            <view class="recommend-tags">
              <view 
                class="recommend-tag" 
                v-for="tag in recommendedTags" 
                :key="tag"
                @tap="addRecommendedTag(tag)"
              >
                <text class="recommend-tag-text">{{ tag }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 删除按钮（仅编辑模式） -->
      <view class="form-section" v-if="isEdit">
        <view class="form-card">
          <view class="delete-btn" @tap="deleteRoute">
            <image src="/static/icons/general/delete.png" class="delete-icon" mode="aspectFit"></image>
            <text class="delete-text">删除路线</text>
          </view>
        </view>
      </view>

      <!-- 底部安全区域 -->
      <view class="safe-area"></view>
    </scroll-view>

    <!-- 底部操作区域 -->
    <view class="bottom-actions">
      <view class="action-buttons">
        <view class="action-btn cancel" @tap="goBack">
          <text class="btn-text">取消</text>
        </view>
        <view class="action-btn save" @tap="saveRoute">
          <text class="btn-text">保存</text>
        </view>
      </view>
    </view>

    <!-- 加载状态 -->
    <view class="loading-mask" v-if="loading">
      <view class="loading-content">
        <image src="/static/icons/general/loading.png" class="loading-icon" mode="aspectFit"></image>
        <text class="loading-text">保存中...</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      isEdit: false,
      routeId: null,
      loading: false,
      scrollHeight: 0,
      newTag: '',
      
      formData: {
        name: '',
        description: '',
        duration: 3,
        distance: '',
        places: [''],
        tags: []
      },
      
      recommendedTags: ['经典', '自然', '文化', '美食', '城市', '海滨', '骑行', '休闲', '徒步', '摄影']
    }
  },
  onLoad(options) {
    this.calculateScrollHeight()
    if (options.id) {
      this.isEdit = true
      this.routeId = parseInt(options.id)
      this.loadRouteData()
    } else {
      this.isEdit = false
    }
  },
  onReady() {
    // 确保页面加载完成后计算正确的高度
    this.calculateScrollHeight()
  },
  onShow() {
    // 页面显示时重新计算高度
    this.$nextTick(() => {
      this.calculateScrollHeight()
    })
  },
  methods: {
    calculateScrollHeight() {
      const systemInfo = uni.getSystemInfoSync()
      const windowHeight = systemInfo.windowHeight
      // 计算头部高度（180rpx转换为px）
      const headerHeight = 180 / 750 * systemInfo.windowWidth
      // 计算底部操作区域高度（约120rpx）
      const bottomHeight = 120 / 750 * systemInfo.windowWidth
      // 计算安全区域
      const safeArea = systemInfo.safeAreaInsets ? systemInfo.safeAreaInsets.bottom : 0
      
      this.scrollHeight = windowHeight - headerHeight - bottomHeight - safeArea
    },
    
    onInputFocus() {
      // 输入框获得焦点时，确保内容可见
      setTimeout(() => {
        this.calculateScrollHeight()
      }, 300)
    },
    
    onInputBlur() {
      // 输入框失去焦点时，恢复高度
      setTimeout(() => {
        this.calculateScrollHeight()
      }, 300)
    },
    
    loadRouteData() {
      try {
        const routes = uni.getStorageSync('user_routes') || []
        const route = routes.find(r => r.id === this.routeId)
        
        if (route) {
          this.formData = {
            name: route.name || '',
            description: route.description || '',
            duration: route.duration || 3,
            distance: route.distance ? route.distance.toString() : '',
            places: route.places && route.places.length > 0 ? [...route.places] : [''],
            tags: route.tags || []
          }
        } else {
          uni.showToast({
            title: '路线不存在',
            icon: 'none'
          })
          setTimeout(() => {
            uni.navigateBack()
          }, 1500)
        }
      } catch (error) {
        console.error('加载路线数据失败:', error)
        uni.showToast({
          title: '加载失败',
          icon: 'none'
        })
      }
    },
    
    goBack() {
      uni.navigateBack()
    },
    
    // 天数操作
    increaseDuration() {
      if (this.formData.duration < 30) {
        this.formData.duration++
      }
    },
    
    decreaseDuration() {
      if (this.formData.duration > 1) {
        this.formData.duration--
      }
    },
    
    // 地点操作
    addPlace() {
      if (this.formData.places.length < 10) {
        this.formData.places.push('')
      } else {
        uni.showToast({
          title: '最多添加10个地点',
          icon: 'none'
        })
      }
    },
    
    removePlace(index) {
      if (this.formData.places.length > 1) {
        this.formData.places.splice(index, 1)
      }
    },
    
    movePlaceUp(index) {
      if (index > 0) {
        const temp = this.formData.places[index]
        this.formData.places.splice(index, 1)
        this.formData.places.splice(index - 1, 0, temp)
      }
    },
    
    movePlaceDown(index) {
      if (index < this.formData.places.length - 1) {
        const temp = this.formData.places[index]
        this.formData.places.splice(index, 1)
        this.formData.places.splice(index + 1, 0, temp)
      }
    },
    
    // 标签操作
    addTag() {
      if (this.newTag.trim() && this.formData.tags.length < 5) {
        if (!this.formData.tags.includes(this.newTag.trim())) {
          this.formData.tags.push(this.newTag.trim())
          this.newTag = ''
        } else {
          uni.showToast({
            title: '标签已存在',
            icon: 'none'
          })
        }
      } else if (this.formData.tags.length >= 5) {
        uni.showToast({
          title: '最多添加5个标签',
          icon: 'none'
        })
      }
    },
    
    removeTag(index) {
      this.formData.tags.splice(index, 1)
    },
    
    addRecommendedTag(tag) {
      if (this.formData.tags.length < 5) {
        if (!this.formData.tags.includes(tag)) {
          this.formData.tags.push(tag)
        } else {
          uni.showToast({
            title: '标签已存在',
            icon: 'none'
          })
        }
      } else {
        uni.showToast({
          title: '最多添加5个标签',
          icon: 'none'
        })
      }
    },
    
    // 保存路线
    async saveRoute() {
      // 表单验证
      if (!this.formData.name.trim()) {
        uni.showToast({
          title: '请输入路线名称',
          icon: 'none'
        })
        return
      }
      
      if (!this.formData.description.trim()) {
        uni.showToast({
          title: '请输入路线描述',
          icon: 'none'
        })
        return
      }
      
      if (!this.formData.distance || parseFloat(this.formData.distance) <= 0) {
        uni.showToast({
          title: '请输入有效的里程数',
          icon: 'none'
        })
        return
      }
      
      // 检查地点是否都填写了
      const emptyPlace = this.formData.places.findIndex(place => !place.trim())
      if (emptyPlace !== -1) {
        uni.showToast({
          title: `请输入第${emptyPlace + 1}个地点`,
          icon: 'none'
        })
        return
      }
      
      this.loading = true
      
      try {
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        let routes = uni.getStorageSync('user_routes') || []
        
        if (this.isEdit) {
          // 编辑模式 - 更新现有路线
          const index = routes.findIndex(r => r.id === this.routeId)
          if (index !== -1) {
            routes[index] = {
              ...routes[index],
              ...this.formData,
              distance: parseFloat(this.formData.distance),
              places: this.formData.places.map(place => place.trim())
            }
          }
        } else {
          // 创建模式 - 添加新路线
          const newId = routes.length > 0 ? Math.max(...routes.map(r => r.id)) + 1 : 1
          const newRoute = {
            id: newId,
            ...this.formData,
            distance: parseFloat(this.formData.distance),
            places: this.formData.places.map(place => place.trim()),
            createTime: new Date().toISOString(),
            // 添加默认数据以在路线列表页显示
            title: this.formData.name,
            rating: 4.5,
            image: '/static/images/routes/default.jpg',
            highlights: ['精心设计的路线', '丰富的景点安排'],
            collectedCount: 0,
            completedCount: 0,
            recommendCount: 0,
            isFavorite: false,
            isOwner: true,
            author: {
              name: '我',
              avatar: '/static/images/avatars/user-default.jpg',
              isOfficial: false
            }
          }
          routes.push(newRoute)
        }
        
        uni.setStorageSync('user_routes', routes)
        
        uni.showToast({
          title: this.isEdit ? '保存成功' : '创建成功',
          icon: 'success'
        })
        
        // 保存成功后跳转回路线列表页
        setTimeout(() => {
          // 使用reLaunch确保回到路线列表页并刷新数据
          uni.reLaunch({
            url: '/pages/route/route'
          })
        }, 1500)
        
      } catch (error) {
        console.error('保存路线失败:', error)
        uni.showToast({
          title: '保存失败',
          icon: 'none'
        })
      } finally {
        this.loading = false
      }
    },
    
    // 删除路线
    deleteRoute() {
      uni.showModal({
        title: '删除路线',
        content: '确定要删除这条路线吗？此操作不可恢复。',
        confirmColor: '#ff6b6b',
        success: (res) => {
          if (res.confirm) {
            this.performDeleteRoute()
          }
        }
      })
    },
    
    async performDeleteRoute() {
      try {
        let routes = uni.getStorageSync('user_routes') || []
        routes = routes.filter(route => route.id !== this.routeId)
        uni.setStorageSync('user_routes', routes)
        
        uni.showToast({
          title: '删除成功',
          icon: 'success'
        })
        
        setTimeout(() => {
          uni.reLaunch({
            url: '/pages/route/route'
          })
        }, 1500)
      } catch (error) {
        console.error('删除路线失败:', error)
        uni.showToast({
          title: '删除失败',
          icon: 'none'
        })
      }
    }
  }
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #b8d4ff 0%, #8bb9ff 100%);
}

/* 页面头部 - 调整标题位置 */
.page-header {
  position: relative;
  height: 160rpx; /* 减小头部高度 */
  overflow: hidden;
}

.header-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #b8d4ff 0%, #8bb9ff 100%);
}

.header-content {
  position: relative;
  z-index: 2;
  padding: 80rpx 30rpx 20rpx; /* 调整内边距，标题上移 */
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-back {
  width: 60rpx;
  height: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-icon {
  width: 24rpx;
  height: 24rpx;
}

.header-title {
  font-size: 36rpx; /* 增大字体 */
  font-weight: 700;
  color: #2c5282;
  text-shadow: 0 2rpx 8rpx rgba(255, 255, 255, 0.5);
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
}

.header-actions {
  display: flex;
  gap: 20rpx;
  /* 已删除保存按钮，此处留空保持布局 */
  width: 60rpx; /* 保持与左侧返回按钮对称 */
}

/* 内容区域 - 调整上边距 */
.content-scroll {
  margin-top: -20rpx; /* 减小上边距 */
  border-top-left-radius: 40rpx;
  border-top-right-radius: 40rpx;
  background: #f0f7ff;
  position: relative;
  z-index: 3;
}

/* 表单区域 */
.form-section {
  background: transparent;
  margin: 24rpx;
}

.section-title {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
  flex-wrap: wrap;
}

.section-icon {
  width: 32rpx;
  height: 32rpx;
  margin-right: 12rpx;
  opacity: 0.8;
}

.section-title-text {
  font-size: 30rpx;
  font-weight: 700;
  color: #2c5282;
  margin-right: 16rpx;
}

.section-subtitle {
  font-size: 24rpx;
  color: #5a7ca8;
  font-weight: 400;
}

.form-card {
  background: #ffffff;
  border-radius: 20rpx;
  padding: 32rpx;
  box-shadow: 0 6rpx 24rpx rgba(184, 212, 255, 0.3);
  border: 1rpx solid #e1edff;
}

/* 表单项 */
.form-item {
  margin-bottom: 32rpx;
  position: relative;
}

.form-item:last-child {
  margin-bottom: 0;
}

.form-label {
  font-size: 28rpx;
  font-weight: 600;
  color: #2c5282;
  display: block;
  margin-bottom: 16rpx;
}

.form-input {
  background: #f8fbff;
  border: 2rpx solid #e1edff;
  border-radius: 12rpx;
  padding: 24rpx;
  font-size: 28rpx;
  color: #2c5282;
  width: 100%;
  box-sizing: border-box;
  line-height: 1.4;
  min-height: 80rpx;
}

.form-textarea {
  background: #f8fbff;
  border: 2rpx solid #e1edff;
  border-radius: 12rpx;
  padding: 24rpx;
  font-size: 28rpx;
  color: #2c5282;
  width: 100%;
  height: 160rpx;
  box-sizing: border-box;
  line-height: 1.4;
}

.placeholder {
  color: #a0bcd8;
  font-size: 28rpx;
}

.char-count {
  position: absolute;
  right: 0;
  bottom: -40rpx;
  font-size: 22rpx;
  color: #a0bcd8;
}

/* 数字输入 */
.number-input {
  display: flex;
  align-items: center;
  background: #f8fbff;
  border: 2rpx solid #e1edff;
  border-radius: 12rpx;
  padding: 0;
  overflow: hidden;
  height: 80rpx;
}

.number-btn {
  width: 80rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(184, 212, 255, 0.3);
  font-size: 32rpx;
  color: #2c5282;
  font-weight: 600;
}

.number-value {
  flex: 1;
  text-align: center;
  font-size: 28rpx;
  color: #2c5282;
  font-weight: 600;
}

/* 地点列表 */
.places-list {
  margin-bottom: 24rpx;
}

.place-item {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
  padding: 20rpx;
  background: #f8fbff;
  border-radius: 12rpx;
  border: 1rpx solid #e1edff;
}

.place-item:last-child {
  margin-bottom: 0;
}

.place-order {
  width: 120rpx;
  flex-shrink: 0;
}

.order-text {
  font-size: 22rpx;
  color: #5a7ca8;
  font-weight: 500;
}

.place-input {
  flex: 1;
  background: transparent;
  border: none;
  font-size: 28rpx;
  color: #2c5282;
  padding: 0 20rpx;
  min-height: 60rpx;
  line-height: 1.4;
}

.place-actions {
  display: flex;
  gap: 8rpx;
}

.action-btn {
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8rpx;
  transition: all 0.3s ease;
}

.action-btn:active {
  transform: scale(0.95);
}

.action-btn.up, .action-btn.down {
  background: rgba(184, 212, 255, 0.3);
  border: 1rpx solid #b8d4ff;
}

.action-btn.delete {
  background: rgba(255, 107, 107, 0.1);
  border: 1rpx solid #ff6b6b;
}

.action-icon {
  width: 20rpx;
  height: 20rpx;
}

/* 添加地点按钮 */
.add-place-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24rpx;
  background: rgba(184, 212, 255, 0.2);
  border: 2rpx dashed #b8d4ff;
  border-radius: 12rpx;
  transition: all 0.3s ease;
}

.add-place-btn:active {
  background: rgba(184, 212, 255, 0.3);
}

.add-icon {
  width: 24rpx;
  height: 24rpx;
  margin-right: 12rpx;
}

.add-text {
  font-size: 26rpx;
  color: #2c5282;
  font-weight: 500;
}

.place-limit-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20rpx;
  background: rgba(184, 212, 255, 0.1);
  border-radius: 12rpx;
}

.limit-text {
  font-size: 24rpx;
  color: #5a7ca8;
}

/* 标签输入 */
.tag-input-container {
  display: flex;
  align-items: center;
  margin-bottom: 24rpx;
}

.tag-input {
  flex: 1;
  background: #f8fbff;
  border: 2rpx solid #e1edff;
  border-radius: 12rpx;
  padding: 20rpx 24rpx;
  font-size: 26rpx;
  color: #2c5282;
  margin-right: 16rpx;
  min-height: 80rpx;
  line-height: 1.4;
}

.add-tag-btn {
  padding: 20rpx 32rpx;
  background: linear-gradient(135deg, #b8d4ff 0%, #8bb9ff 100%);
  border-radius: 12rpx;
  box-shadow: 0 3rpx 12rpx rgba(139, 185, 255, 0.4);
}

.add-tag-text {
  font-size: 26rpx;
  color: #2c5282;
  font-weight: 600;
}

/* 标签列表 */
.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  margin-bottom: 24rpx;
  min-height: 60rpx;
}

.tag-item {
  display: flex;
  align-items: center;
  background: rgba(184, 212, 255, 0.3);
  padding: 12rpx 20rpx;
  border-radius: 20rpx;
  border: 1rpx solid rgba(184, 212, 255, 0.5);
}

.tag-text {
  font-size: 24rpx;
  color: #2c5282;
  font-weight: 500;
  margin-right: 8rpx;
}

.tag-remove {
  width: 28rpx;
  height: 28rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
}

.remove-icon {
  width: 12rpx;
  height: 12rpx;
}

.no-tags {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 20rpx;
}

.no-tags-text {
  font-size: 24rpx;
  color: #a0bcd8;
  font-style: italic;
}

/* 推荐标签 */
.recommended-tags {
  border-top: 1rpx solid #e1edff;
  padding-top: 24rpx;
}

.recommend-title {
  font-size: 24rpx;
  color: #5a7ca8;
  font-weight: 500;
  display: block;
  margin-bottom: 16rpx;
}

.recommend-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.recommend-tag {
  background: rgba(184, 212, 255, 0.2);
  padding: 12rpx 20rpx;
  border-radius: 16rpx;
  border: 1rpx solid rgba(184, 212, 255, 0.4);
  transition: all 0.3s ease;
}

.recommend-tag:active {
  background: rgba(184, 212, 255, 0.4);
}

.recommend-tag-text {
  font-size: 22rpx;
  color: #2c5282;
  font-weight: 500;
}

/* 删除按钮 */
.delete-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24rpx;
  background: rgba(255, 107, 107, 0.1);
  border: 2rpx solid #ff6b6b;
  border-radius: 12rpx;
  transition: all 0.3s ease;
}

.delete-btn:active {
  background: rgba(255, 107, 107, 0.2);
}

.delete-icon {
  width: 28rpx;
  height: 28rpx;
  margin-right: 12rpx;
}

.delete-text {
  font-size: 26rpx;
  color: #ff6b6b;
  font-weight: 600;
}

/* 底部操作区域 - 固定在底部 */
.bottom-actions {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #f0f7ff;
  padding: 20rpx 30rpx;
  border-top: 1rpx solid #e1edff;
  z-index: 10;
  /* 添加安全区域支持 */
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
}

.action-buttons {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 20rpx;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24rpx;
  border-radius: 16rpx;
  font-weight: 600;
  transition: all 0.3s ease;
}

.action-btn:active {
  transform: scale(0.98);
}

.action-btn.cancel {
  background: #ffffff;
  border: 2rpx solid #b8d4ff;
  color: #2c5282;
}

.action-btn.save {
  background: linear-gradient(135deg, #b8d4ff 0%, #8bb9ff 100%);
  border: 2rpx solid #8bb9ff;
  color: #2c5282;
  box-shadow: 0 4rpx 12rpx rgba(139, 185, 255, 0.4);
}

.btn-text {
  font-size: 28rpx;
  font-weight: 600;
}

/* 加载状态 */
.loading-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(184, 212, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-content {
  background: #ffffff;
  padding: 32rpx;
  border-radius: 18rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 6rpx 24rpx rgba(184, 212, 255, 0.4);
  border: 1rpx solid #e1edff;
}

.loading-icon {
  width: 70rpx;
  height: 70rpx;
  margin-bottom: 16rpx;
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 26rpx;
  color: #5a7ca8;
  font-weight: 500;
}

/* 安全区域 */
.safe-area {
  height: env(safe-area-inset-bottom);
  background: #f0f7ff;
}
</style>