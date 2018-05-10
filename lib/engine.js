const path = require('path')
const grpc = require('grpc')

const DEPLOY_STORY = process.env.STORY || 'stories/app/release/new.story'
const ENGINE = process.env.ENGINE || 'engine:50051'
const PROTO_PATH = path.join(__dirname, 'engine.proto')

const Client = grpc.load(PROTO_PATH).HttpProxy

const Engine = new Client(ENGINE, grpc.credentials.createInsecure())


function run(client, data){
  Engine.RunStory({
    'story_name': DEPLOY_STORY,
    'json_context': data
  }).on('data', (data) => {
    // write('{"data":""}')
    if (data.startsWith('write(')) {
      data = JSON.parse(data.slice(6, -1))
      client.write(data['data'])

    // error('{"code":200, "message": ""}')
    } else if (data.startsWith('error(')) {
      data = JSON.parse(data.slice(6, -1))
      client.writeHead(parseInt(data['code']), data['message'])

    // finish()
    } else if (data.startsWith('finish(')) {
      client.end()
    }
  }).on('error', (e) => {
  })

}
