<template>
    <v-row class="device-selector pa-4">
        <v-col cols="12" class="title">
            <span>Device Selector</span>
        </v-col>
        <v-col cols="12">
            <v-row align="center" justify="center">
                <v-col cols="12" md="6" class="d-flex align-center ga-3">
                    <v-row class="d-flex ga-3">
                        <v-col class="d-flex">
                            <v-select
                                label="Choose device"
                                v-model="selectedDevice"
                                :items="devices"
                                :disabled="loadingDevices"
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
                            ></v-select>
                        </v-col>
                    </v-row>    
                </v-col>
                <v-col cols="12" class="d-flex justify-center ga-3">
                    <v-btn color="primary" @click="fetchDevicesData" :disabled="loadingDevices">Reload</v-btn>
                    <v-btn color="error" @click="$emit('delete-config')">Delete Config</v-btn>
                </v-col>
            </v-row>
        </v-col>
    </v-row>
</template>

<script>
import { ref, watch } from 'vue';
import { fetchDevices, fetchDeviceIp } from '../utils/specific.js';

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
            this.selectedDevice = "";
            this.loadingDevices = true;
            try {
                const { data } = await fetchDevices();
                this.devices = data;
                if (data.length > 0 && !this.selectedDevice) {
                    this.selectedDevice = data[0];
                    this.$emit('update:device', this.selectedDevice);
                }
                else {
                    this.selectedDevice = "";
                    this.selectedIp = "";
                    this.ips = [];
                }
            } catch (err) {
            } finally {
                this.loadingDevices = false;
            }
        },
        async fetchDeviceIps(device) {
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
                    this.selectedIp = this.ips[0].ip;
                }
            } catch (err) {
                alert(`[GET] Ips error: ${err.message}`);
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
            this.$emit('update:deviceIp', newVal);
        },
    },
    created() {
        this.fetchDevicesData();
    },
};
</script>