CloudFormationデプロイコマンド
```
aws cloudformation deploy \
  --template-file csvUploadVue.yaml \
  --stack-name csv-upload-sample \
  --capabilities CAPABILITY_NAMED_IAM \
  --region ap-northeast-3
```

Vueサーバー起動
```
cd csv-upload-front/
npm run dev
```