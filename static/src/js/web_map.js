odoo.define('transhybrid_jakarta.FieldMap', function(require) {
"use strict";

var core = require('web.core');
var form_common = require('web.form_common');

var FieldMap = form_common.AbstractField.extend({
    template: 'FieldMap',
    start: function() {
        var self = this;

        this.map = new google.maps.Map(this.el, {
            center: {lat:0,lng:0},
            zoom: 0,
            //mapTypeId: google.maps.MapTypeId.ROADMAP,
            //disableDefaultUI: true,
        });

        
        this.bounds  = new google.maps.LatLngBounds();

        this.marker = new google.maps.Marker({
            position: {lat:0,lng:0},
        });

        this.geoXmlParser = new geoXML3.parser({
           map:this.map
        });

        this.flightPath = new google.maps.Polyline({
          path: [],
          geodesic: true,
          //strokeColor: '#FF0000',
          strokeOpacity: 1.0,
          strokeWeight: 2
        });

        
        this.getParent().$('a[data-toggle="tab"]').on('shown.bs.tab', function() {
            self.trigger('resize');
        });
        this.getParent().on('attached', this.getParent(), function() {
            self.trigger('resize');
        });

        this.on('change:effective_readonly', this, this.update_mode);
        this.on('resize', this, this._toggle_label);
        this.update_mode();
        this._super();
    },
    render_value: function() {
        if(this.get_value()) {
            

            this.map = new google.maps.Map(this.el, {
                center: {lat:0,lng:0},
                zoom: 0
            });

                        
            if(JSON.parse(this.get_value()).is_kml){

                var labels = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
                var labelIndex = 0;

                this.geoXmlParser = new geoXML3.parser({
                    map:this.map
                });

                var panjang = JSON.parse(this.get_value()).all_kml_file
                var index;
                
                for(index = 0;index<panjang.length; index++){

                    this.geoXmlParser.parseKmlString(JSON.parse(this.get_value()).all_kml_file[index]);

                }

                var panjangTaskPosition = JSON.parse(this.get_value()).position_task;
                var loc,a;

                panjangTaskPosition = panjangTaskPosition.length;

                for (a = 0; a<panjangTaskPosition; a++){
                    loc = new google.maps.LatLng(JSON.parse(this.get_value()).position_task[a]['lat'],JSON.parse(this.get_value()).position_task[a]['lng']);
                    this.bounds.extend(loc);

                    this.marker = new google.maps.Marker({
                            position: new google.maps.LatLng(JSON.parse(this.get_value()).position_task[a]['lat'],JSON.parse(this.get_value()).position_task[a]['lng']),
                            label: labels[labelIndex++ % labels.length]                    
                        }); 

                    this.marker.setMap(this.map);
                }


                // ======= ORIGINAL CODE
                this.map.fitBounds(this.bounds);       
                this.map.panToBounds(this.bounds);

                if(this.map.getZoom()<=5){
                    this.map.setZoom(8);
                }


            }


        } else {

            // PERTAMA..........
            this.marker.setPosition({lat:0,lng:0});
            this.map.setCenter({lat:0,lng:0});
            this.map.setZoom(2);
            this.marker.setMap(null);
                        
        }
    },
    update_mode: function() {
        if(this.get("effective_readonly")) {

            this.map.setOptions({
                disableDoubleClickZoom: true,
                draggable: false,
                scrollwheel: false,
            });
            
            this.marker.setOptions({
                draggable: false,
                cursor: 'default',
            });            

        } else {

            this.map.setOptions({
                disableDoubleClickZoom: false,
                draggable: true,
                scrollwheel: true,
            });

            
            this.marker.setOptions({
                //draggable: true,
                draggable: false,
                cursor: 'pointer',
            });
            
        }
    },
    _toggle_label: function() {
        this._super();
        google.maps.event.trigger(this.map, 'resize');
        if (!this.no_rerender) {
            this.render_value();
        }
    },
});

core.form_widget_registry.add('map', FieldMap);

return {
    FieldMap: FieldMap,
};

});