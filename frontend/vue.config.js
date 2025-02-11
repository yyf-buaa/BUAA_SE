module.exports = {
    publicPath: '/admin/',
    devServer: {
        //open: true,
        //host: 'localhost',
        //port: 9000,
        //https: false,
        //以上的ip和端口是我们本机的;下面为需要跨域的
        proxy: {  //配置跨域
            '/api': {
                //target: 'https://tra-fr-2.zhouyc.cc/',  //这里后台的地址模拟的;应该填写你们真实的后台接口
                target: 'http://114.116.197.121:9000/',
		// ws: true,
                changOrigin: true,  //允许跨域
                pathRewrite: {
                    '^/api': ''  //请求的时候使用这个api就可以
                }
            }
        },
    },
}
