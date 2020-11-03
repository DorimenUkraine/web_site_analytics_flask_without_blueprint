var cmb = new Object;

cmb.readCookie = function(name) {
	var nameEQ = name + "=";
	var ca = document.cookie.split(';');
	for(var i=0;i < ca.length;i++) {
    var c = ca[i];
		while (c.charAt(0)==' '){
      c = c.substring(1,c.length);
    }
		if (c.indexOf(nameEQ) == 0){
      return c.substring(nameEQ.length,c.length);
    };
	}
 return null;
};

cmb.getRequest = function(props){
  var qstr = '';
  for (var prop in props) {
    qstr += prop+"="+encodeURIComponent(props[prop])+'&';
  }
  qstr = qstr.substring(0, qstr.length - 1);
  var img = new Image;
  var proto = window.location.protocol;
  var gif_id = Math.round(2147483647 * Math.random());
  img.src = proto + '//{{ domain }}/' + gif_id + '.gif?' + qstr;
};

cmb.event = function(name, value){
  var cid = this.readCookie('cid'),
      session = sessionStorage.getItem("session");
  var props = {
    v:1,
    t:'event',
    cid,
    session,
    ul:window.navigator.userLanguage || window.navigator.language,
    sd:screen.colorDepth+'-bit',
    sr:screen.width+'x'+screen.height,
    de:document.characterSet,
    dl:document.location.href,
    dt:document.title,
    dr:document.referrer,
    en:name,
    ev:value
  };
  this.getRequest(props)
};

cmb.onClick = function(e) {
	if (e.target && e.target.id) {
		// console.log(`${e.target.id} was clicked`);
	    this.event("click", e.target.id);
	}
}

function getRandom(max) {
    return Math.round((max-1) * Math.random() + 1);
}

function start() {
  var cid = cmb.readCookie('cid'),
      session = sessionStorage.getItem("session");
  if(!cid) {
    cid = getRandom(2147483647);
    document.cookie = 'cid='+cid;
  }
  if(!session) {
      session = getRandom(2147483647);
      sessionStorage.setItem("session", session);
  }
  var props = {v:1,
               t:'visit',
               cid,
               session,
               ul:window.navigator.userLanguage || window.navigator.language,
               sd:screen.colorDepth+'-bit',
               sr:screen.width+'x'+screen.height,
               de:document.characterSet,
               dl:document.location.href,
               dt:document.title,
               dr:document.referrer};
  cmb.getRequest(props);

  window.addEventListener("click", listener(cmb.onClick, cmb));
}

function listener(f, context) {
    return function(e) {
        f.call(context, e);
    }
}

start();