let cacheData = "lastMile";
this.addEventListener("install",(e)=>{
    e.waitUntill(
        caches.open(cacheData).then((cache)=>{
            cache.addAll
        })
    )
})


