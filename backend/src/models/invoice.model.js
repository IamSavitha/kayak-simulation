
const mongoose = require('mongoose');   

const invoiceSchema = new mongoose.Schema({
  billingId: { type: Number, required: true, index: true },
  invoiceNumber: { type: String, required: true, unique: true },
  generatedAt: { type: Date, default: Date.now },
  payload: {
    type: Object,
    required: true
  },
  pdfUrl: { type: String }
});

module.exports = mongoose.model('Invoice', invoiceSchema);
