// Johnny Tour Website - Language Switcher (Chinese / English)
const LANG = {
  zh: {
    'hero-sub': '探索美西壮美自然风光',
    'hero-desc': '多条精品线路，带你深入美西最震撼的自然景观',
    'hero-btn1': '探索线路',
    'hero-btn2': '景点相册',
    'tours-label': '精选线路',
    'tours-title': '多条精品线路',
    'tours-desc': '从黄石公园到羚羊彩穴，从大峡谷到优胜美地，每一条线路都是精心设计的深度体验之旅',
    'update-text': '🔄 不定期更新精选路线 · 每天发掘好团行程',
    'consult': '立即咨询',
    'detail': '查看详情',
    'download': '下载详细路线',
    'more-label': '更多选择',
    'more-title': '更多团型 · 全球线路',
    'more-desc': '除了以上标准行程，我们还有更多选择适合您的需求，欢迎通过地图查阅然后咨询',
    'map-hint': '💡 鼠标滚轮缩放 · 拖拽查看',
    'badge-premium': '精品小团',
    'badge-hot': '热卖',
    'badge-classic': '经典线路',
    'badge-recommended': '推荐',
    'price-single': '单人入住',
    'price-double': '两人入住',
    'price-triple': '三人入住',
    'price-quad': '四人入住',
    'bus-title': '大巴团',
    'bus-desc': '经济实惠、结伴出行、标准行程',
    'bus-f1': '✓ 价格优惠，适合个人、情侣',
    'bus-f2': '✓ 标准行程，固定出发日期',
    'bus-f3': '✓ 结识旅伴，欢乐同行',
    'premium-title': '精品小团',
    'premium-desc': '6-12人、高顶商务、灵活舒适',
    'premium-f1': '✓ 精品小团，体验更私密',
    'premium-f2': '✓ 高顶商务，空间宽敞',
    'premium-f3': '✓ 两人即可成团，灵活出发',
    'custom-title': '定制包团',
    'custom-desc': '私人专属、自由搭配、专属导游',
    'custom-f1': '✓ 专属行程，自由组合景点',
    'custom-f2': '✓ 专属导游，全程贴心服务',
    'custom-f3': '✓ 企业团队、家庭包团首选',
    'type-consult': '欢迎电话/微信咨询',
    'features-label': '服务优势',
    'features-title': '为什么选择我们',
    'features-desc': '多年深耕美国旅游线路，为您打造无忧的深度旅行体验',
    'feat1-title': '尊享体验',
    'feat1-desc': '大巴，精品小团，订制包团，VIP级别旅行体验，拒绝走马观花',
    'feat2-title': '多年经验',
    'feat2-desc': '连续超过15年热卖经典线路，经验丰富，服务可靠',
    'feat3-title': '诚信为本',
    'feat3-desc': '我们始终秉持诚实与透明的原则，坚守行业底线与品牌信誉。',
    'feat4-title': '贴心服务',
    'feat4-desc': '我们懂两种语言，更懂您一份安心。全程照顾，尊享出行',
    'fleet-label': '我们的车队',
    'fleet-title': '关于我们车队',
    'fleet-desc': '从高端商务用车到大型豪华巴士，一站式满足不同出行需求',
    'fleet1-title': '14-15座高顶商务车',
    'fleet1-desc': '高顶设计,轻松进出。商务级内饰,舒适私密。小型包团与家庭出游首选。',
    'fleet2-title': '38-40座中型巴士',
    'fleet2-desc': '高顶设计,轻松进出。商务级内饰,舒适私密。中小型团队出游首选。',
    'fleet3-title': '7座高端商务车',
    'fleet3-desc': '空间宽绰,上下自如。豪华内饰,私享舒适。精品小团与家庭出游首选。',
    'fleet4-title': '56座豪华大巴',
    'fleet4-desc': '宽敞空间,舒适出行。豪华设施,平稳安静。大型团队与长途旅行首选。',
    'fleet-t1': '高顶设计', 'fleet-t2': '商务内饰', 'fleet-t3': '舒适私密',
    'fleet-t4': '轻松进出', 'fleet-t5': '空间宽绰', 'fleet-t6': '豪华内饰',
    'fleet-t7': '私享舒适', 'fleet-t8': '56座超大', 'fleet-t9': '超大行李舱',
    'fleet-t10': '车载洗手间',
    'contact-title': '联系方式',
    'contact-desc': '选择您方便的方式，我们随时为您解答',
    'phone': '电话咨询',
    'whatsapp': '扫码添加WhatsApp',
    'wechat': '微信咨询',
    'xhs': '小红书',
    'email': '邮件咨询',
    'send-email': '发送邮件',
    'copy-email': '复制邮箱地址',
    'copied': '已复制!',
    'form-title': '留言预订/咨询',
    'form-desc': '填写以下信息，我们会尽快与您联系',
    'name': '姓名',
    'phone-f': '电话',
    'email-f': '邮箱',
    'wechat-f': '微信号',
    'date': '期望出行日期',
    'guests': '出行人数',
    'guests-select': '请选择人数',
    'guest-1': '1人', 'guest-2': '2人', 'guest-3': '3人', 'guest-4': '4人', 'guest-5': '5人以上',
    'message': '备注留言',
    'submit': '提交预订咨询',
    'close-qr': '点击任意位置关闭',
    'footer': '© 2026 尊享旅行. JJ Tour LLC.',
    'modal-features': '行程特色',
    'modal-price': '价格',
    'modal-dates': '出发班期',
    'modal-route': '途经景点',
    'modal-pickup': '参/离团地点',
    'modal-cta': '立即咨询此线路',
    'lang-btn': 'EN',
    // Navigation
    'nav-explore': '探索线路',
    'nav-gallery': '景点相册',
    'nav-home': '首页',
    'nav-tours': '旅行线路',
    'nav-features': '服务优势',
    'nav-fleet': '关于我们车队',
    'nav-contact': '联系我们',
  },
  en: {
    'hero-sub': 'Discover the American West',
    'hero-desc': 'Premium itineraries into the most stunning natural landscapes',
    'hero-btn1': 'Explore Tours',
    'hero-btn2': 'Photo Gallery',
    'tours-label': 'Featured Tours',
    'tours-title': 'Premium Travel Routes',
    'tours-desc': 'From Yellowstone to Antelope Canyon, every route is a carefully crafted deep experience',
    'update-text': '🔄 New routes added regularly',
    'consult': 'Inquire Now',
    'detail': 'View Details',
    'download': 'Download Itinerary',
    'more-label': 'More Options',
    'more-title': 'More Options',
    'more-desc': 'Beyond these standard routes, we offer more options to suit your needs',
    'map-hint': '💡 Scroll to zoom · Drag to pan',
    'badge-premium': 'Premium Small Group',
    'badge-hot': 'Hot Seller',
    'badge-classic': 'Classic Route',
    'badge-recommended': 'Recommended',
    'price-single': 'Single Room',
    'price-double': 'Double Room',
    'price-triple': 'Triple Room',
    'price-quad': 'Quad Room',
    'bus-title': 'Coach Bus',
    'bus-desc': 'Affordable, group travel, fixed schedule',
    'bus-f1': '✓ Budget-friendly, great for solo travelers & couples',
    'bus-f2': '✓ Fixed schedule, standard itineraries',
    'bus-f3': '✓ Meet fellow travelers, enjoy the journey together',
    'premium-title': 'Premium Small Group',
    'premium-desc': '6-12 people, high-roof van, flexible & comfortable',
    'premium-f1': '✓ Intimate small group experience',
    'premium-f2': '✓ Spacious high-roof vehicles',
    'premium-f3': '✓ Departs with just 2 people',
    'custom-title': 'Private Charter',
    'custom-desc': 'Exclusive, customizable, private guide',
    'custom-f1': '✓ Custom itinerary, pick any attractions',
    'custom-f2': '✓ Private guide, dedicated service throughout',
    'custom-f3': '✓ Ideal for corporate teams & family groups',
    'type-consult': 'Call or WeChat for inquiries',
    'features-label': 'Why Choose Us',
    'features-title': 'Our Advantages',
    'features-desc': 'Over 15 years of expertise in US travel',
    'feat1-title': 'Premium Experience',
    'feat1-desc': 'Coach buses, premium small groups, private charters — VIP-level travel',
    'feat2-title': '15+ Years Experience',
    'feat2-desc': 'Consistently popular classic routes for over 15 years',
    'feat3-title': 'Honest & Transparent',
    'feat3-desc': 'We uphold honesty and transparency, maintaining industry standards',
    'feat4-title': 'Caring Service',
    'feat4-desc': 'We speak your language and understand your needs',
    'fleet-label': 'Our Fleet',
    'fleet-title': 'Our Vehicles',
    'fleet-desc': 'From premium vans to luxury coaches',
    'fleet1-title': '14-15 Passenger High-Roof Van',
    'fleet1-desc': 'High-roof design for easy entry. Business-class interior.',
    'fleet2-title': '38-40 Passenger Mid-Size Bus',
    'fleet2-desc': 'High-roof design for easy entry. Great for small-to-medium teams.',
    'fleet3-title': '7-Passenger Premium Van',
    'fleet3-desc': 'Spacious cabin, easy access. Luxury interior.',
    'fleet4-title': '56-Passenger Luxury Coach',
    'fleet4-desc': 'Roomy interior, smooth ride. Premium amenities.',
    'fleet-t1': 'High-Roof', 'fleet-t2': 'Business Interior', 'fleet-t3': 'Comfortable & Private',
    'fleet-t4': 'Easy Access', 'fleet-t5': 'Spacious', 'fleet-t6': 'Luxury Interior',
    'fleet-t7': 'Private Comfort', 'fleet-t8': '56 Seats', 'fleet-t9': 'Large Luggage Bay',
    'fleet-t10': 'Onboard Restroom',
    'contact-title': 'Contact Us',
    'contact-desc': 'Choose your preferred way to reach us',
    'phone': 'Phone',
    'whatsapp': 'WhatsApp',
    'wechat': 'WeChat',
    'xhs': 'Xiaohongshu',
    'email': 'Email',
    'send-email': 'Send Email',
    'copy-email': 'Copy Email',
    'copied': 'Copied!',
    'form-title': 'Booking Inquiry',
    'form-desc': 'Fill in the info below and we will contact you soon',
    'name': 'Name',
    'phone-f': 'Phone',
    'email-f': 'Email',
    'wechat-f': 'WeChat ID',
    'date': 'Travel Date',
    'guests': 'Number of Travelers',
    'guests-select': 'Select number',
    'guest-1': '1 Person', 'guest-2': '2 Persons', 'guest-3': '3 Persons', 'guest-4': '4 Persons', 'guest-5': '5+ Persons',
    'message': 'Message',
    'submit': 'Submit Inquiry',
    'close-qr': 'Click anywhere to close',
    'footer': '© 2026 JJ Tour LLC.',
    'modal-features': 'Highlights',
    'modal-price': 'Pricing',
    'modal-dates': 'Departure Dates',
    'modal-route': 'Route & Attractions',
    'modal-pickup': 'Pickup & Drop-off',
    'modal-cta': 'Inquire About This Tour',
    'lang-btn': '中文',
    'nav-explore': 'Explore Tours',
    'nav-gallery': 'Photo Gallery',
    'nav-home': 'Home',
    'nav-tours': 'Tours',
    'nav-features': 'Why Us',
    'nav-fleet': 'Fleet',
    'nav-contact': 'Contact',
  }
};

let currentLang = localStorage.getItem('jt_lang') || 'zh';

function setLang(lang) {
  if (!LANG[lang]) return;
  currentLang = lang;
  localStorage.setItem('jt_lang', lang);
  document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en';
  
  const t = LANG[lang];
  
  // Update all data-i18n elements
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (t[key] !== undefined) {
      if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
        el.placeholder = t[key];
      } else {
        el.textContent = t[key];
      }
    }
  });
  
  // Update placeholders via data-i18n-ph
  document.querySelectorAll('[data-i18n-ph]').forEach(el => {
    const key = el.getAttribute('data-i18n-ph');
    if (t[key] !== undefined) {
      el.placeholder = t[key];
    }
  });
  
  // Update lang switcher button
  const btn = document.getElementById('lang-switch-btn');
  if (btn) btn.textContent = t['lang-btn'];
}

function toggleLang() {
  setLang(currentLang === 'zh' ? 'en' : 'zh');
}

// Auto-init
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => setLang(currentLang));
} else {
  setLang(currentLang);
}
