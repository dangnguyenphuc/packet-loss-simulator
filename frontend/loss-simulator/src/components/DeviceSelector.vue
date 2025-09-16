<template>
    <v-row class="pa-3" align="center" justify="center">
        <v-col class="d-flex align-center ga-3">
            <v-row class="d-flex ga-3">
                <v-col class="d-flex">
                    <v-select
                        label="Choose device"
                        v-model="selectedDevice"
                        :items="devices"
                        :disabled="loadingDevices"
                        hide-details
                    ></v-select>
                </v-col>
                <v-col class="d-flex">
                    <v-select
                        label="Choose IP"
                        v-model="selectedIp"
                        :items="ips"
                        :disabled="loadingIps"
                        item-title="text"
                        item-value="ip"
                        hide-details
                    ></v-select>
                </v-col>
                <v-col cols="1" class="d-flex justify-center align-center">
                    <v-btn color="primary" icon="mdi-restart" @click="fetchDevicesData" :disabled="loadingDevices"></v-btn>
                </v-col>
            </v-row>    
        </v-col>
    </v-row>
</template>

<script>
import { ref, watch } from 'vue';
import { fetchDevices, fetchDeviceIp } from '../utils/specific.js';
import { 
    EVENT_FETCH_DEVICE,
    EVENT_UPDATE_DEVICE,
    EVENT_UPDATE_DEVICE_IP
 } from '../constants/constant.js';

export default {
    name: 'DeviceSelector',
    props: {
        device: String,
        ip: String,
    },
    data() {
        return {
            
            devices: [],
            ips: [],
            loadingDevices: false,
            loadingIps: false,
            selectedDevice: this.device,
            selectedIp: this.ip,
        };
    },
    methods: {
        async fetchDevicesData() {
            this.$emit(EVENT_FETCH_DEVICE, false);
            this.selectedDevice = "";
            this.loadingDevices = true;
            try {
                const { data } = await fetchDevices();
                this.devices = data;
                if (data.length > 0 && !this.selectedDevice) {
                    this.selectedDevice = data[0];
                    this.$emit(EVENT_UPDATE_DEVICE, this.selectedDevice);                }
                else {
                    this.selectedDevice = "";
                    this.selectedIp = "";
                    this.ips = [];
                    this.$emit(EVENT_FETCH_DEVICE, false);
                }

                // fetch done -> load test info
                
            } catch (err) {
                this.$emit(
                    EVENT_OPEN_TOAST, 
                    "Get devices failed",
                    "Error: " + err.message
                );
            } finally {
                this.loadingDevices = false;
                
            }
        },
        async fetchDeviceIps(device) {
            this.$emit(EVENT_FETCH_DEVICE, false);
            this.selectedIp = "";
            if (!device || device.length === 0) 
            {
                this.ips = [];
                return;
            }
            this.loadingIps = true;
            try {
                const { data } = await fetchDeviceIp(device);
                this.ips = data
                    .filter(ip => ip.ip.startsWith('10.42'))
                    .map(ip => ({ ip: ip.ip, text: `${ip.interface}-${ip.ip}` }));
                if (this.ips.length > 0) {
                    // fetch success
                    this.selectedIp = this.ips[0].ip;
                    this.$emit(EVENT_FETCH_DEVICE, true);
                }
            } catch (err) {
                console.log(err.message)
                this.$emit(
                    EVENT_OPEN_TOAST, 
                    "Get device IP failed",
                    "Error: " + err.message
                );
            } finally {
                this.loadingIps = false;
            }
        },
    },
    watch: {
        selectedDevice(newVal) {
            this.fetchDeviceIps(newVal);
        },
        selectedIp(newVal) {
            this.$emit(EVENT_UPDATE_DEVICE_IP, newVal);
        },
    },
    created() {
        this.fetchDevicesData();
    }

};
</script>