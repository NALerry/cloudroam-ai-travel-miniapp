// utils/weather.js
export default {
  // 获取实时天气
  async getCurrentWeather(city) {
    try {
      const result = await uni.request({
        url: 'https://wis.qq.com/weather/common',
        data: {
          source: 'xw',
          weather_type: 'observe|forecast_1h|forecast_24h|index',
          province: city.province,
          city: city.city,
          county: city.district
        }
      })
      return this.processWeatherData(result.data)
    } catch (error) {
      console.error('获取天气数据失败:', error)
      throw error
    }
  },
  
  // 处理天气数据
  processWeatherData(rawData) {
    return {
      city: rawData.area,
      temperature: rawData.observe.temp,
      desc: rawData.observe.weather,
      humidity: rawData.observe.humidity,
      windSpeed: rawData.observe.wind_speed
    }
  }
}