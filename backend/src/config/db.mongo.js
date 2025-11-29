const mongoose = require('mongoose');

async function connectMongo() {
  const uri = process.env.MONGO_URI || 'mongodb://localhost:27017/kayak';
  await mongoose.connect(uri);
  console.log('Mongo connected');
}

module.exports = connectMongo;
