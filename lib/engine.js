const path = require('path');
const grpc = require('grpc');

const DEPLOY_STORY = process.env.STORY || 'stories/app/release/new.story';
const ENGINE = process.env.ENGINE || 'engine:50051';
const PROTO_PATH = path.join(__dirname, 'engine.proto');

const Client = grpc.load(PROTO_PATH).HttpProxy;

const Engine = new Client(ENGINE, grpc.credentials.createInsecure());


function run(data, callback){
  Engine.RunStory({
    'story_name': DEPLOY_STORY,
    'json_context': data
  }, function (err, res) {
    if (err) {
      return console.log(err);
    }
    console.log('Story started');
    return console.log(res);
  });
}
