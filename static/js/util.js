// 创建一个 Utils 命名空间
var Utils = (function() {
    // 私有函数和变量可以在这里定义
    
    // 返回一个包含公共方法的对象
    return {
        generateUUID: function() {
            return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
                return v.toString(16);
            });
        },
        
        // 你可以在这里添加更多的公共方法
        formatDate: function(date) {
            // 日期格式化逻辑
            return date.toISOString().split('T')[0];
        },
        
        capitalize: function(string) {
            return string.charAt(0).toUpperCase() + string.slice(1);
        }
    };
})();

// 如果你希望某些方法在全局范围内可用,可以这样做:
// window.generateUUID = Utils.generateUUID;

// var uuid = Utils.generateUUID();
// console.log(uuid);

// var formattedDate = Utils.formatDate(new Date());
// console.log(formattedDate);

// var capitalizedString = Utils.capitalize("hello");
// console.log(capitalizedString);