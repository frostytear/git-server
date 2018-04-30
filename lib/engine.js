const path = require('path');
const grpc = require('grpc');

const DEPLOY_STORY = process.env.STORY || 'stories/app/deploy/deploy.story';
const ENGINE = process.env.ENGINE || 'engine:50051';
const PROTO_PATH = path.join(__dirname, '/engine.proto');

const Client = grpc.load(PROTO_PATH).Request;

const getClient = function (address) {
  return new Client(address, grpc.credentials.createInsecure());
};

const engine = getClient(ENGINE);


function run(data, callback){
  engine.start({
    'file': DEPLOY_STORY,
    'data': data
  }, function (err, res) {
    if (err) {
      return console.log(err);
    }
    console.log('Story started');
    return console.log(res);
  });
}
