# Yoka Bot

```sh
scrapy crawl YokaBot -s JOBDIR=cache/YokaBot-0727
grep YokaBotProductItem data/items.jsonlines | wc -l
grep YokaBotProductItem data/items.jsonlines | gawk -F"\n\b" '{
    for(i=1; i<=NF; i++) {
        if(match($i,"product_id\": \"([a-zA-Z0-9\\-_]+)",a)){
            print a[1]
        }
    }
}' | sort | uniq | wc -l
```
