const express = require("express");
const productRoutes = express.Router();
const dbo = require("../db/conn");
const ObjectId = require("mongodb").ObjectId;

productRoutes.get("/product", async(req, res) => {
    const sort_by = req.query.sort;
    let db_connect = await dbo.getDb("storage");
    db_connect.collection("products").find({}).toArray( async (err, result) => {
        if (err) throw err;
        if (!sort_by) {
            return res.send(result)
        }
        const sorted_result = result.sort((a, b) => a[sort_by] - b[sort_by])
        return res.send(sorted_result)
    })
})

productRoutes.get("/product/raport", async(req, res) => {
    let db_connect = await dbo.getDb("storage");
    const my_query = {}
    db_connect.collection("products").find({}).toArray( async (err, result) => {
        if (err) throw err;
        const raport = await result.map(product => {
            return {
                name: product.name,
                amount: product.amount,
                value: product.amount*product.prize
            }
        })
        res.send(raport)
    })
})

productRoutes.post("/product", async (req, res) => {
    const to_add = {
        name: req.body.name,
        prize: req.body.prize,
        amount: req.body.amount,
        unit: req.body.unit,
        description: req.body.description
    }
    
    let db_connect = await dbo.getDb("storage");
    db_connect.collection("products").findOne({name: new RegExp('^'+to_add.name+'$', "i")}, function(err, doc) {
        if (doc) {
            return res.send("Product alredy exists")
        }
        db_connect.collection("products").insertOne(to_add, async(err, result) => {
            if (err) throw err;
            res.send(result)
        })
      });
})


productRoutes.put("/product/:id", async(req, res) => {
    let db_connect = await dbo.getDb("storage");
    const my_query = {_id: ObjectId(req.params.id)};
    const newValues = {
        $set: {
            name: req.body.name,
            prize: req.body.prize,
            amount: req.body.amount,
            unit: req.body.unit,
            description: req.body.description
        },
    };
    db_connect.collection("products").updateOne(my_query, newValues, async(err, result) => {
        if (err) throw err;
        res.send(result)
    })
})

productRoutes.delete("/product/:id", async(req, res) => {
    let db_connect = await dbo.getDb("storage");
    const my_query = {_id: ObjectId(req.params.id)};
    db_connect.collection("products").deleteOne(my_query, async(err, result) => {
        if (err) console.log(err);;
        res.send(result)
    })
})


module.exports = productRoutes;