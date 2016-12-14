function parseInterval(value) {
/**
 * Takes time given in seconds and returns it in Date format
 * @param {28800} value
 * @return {1, 1, 1, 8, 0, 0} result 
 */
    var result = new Date(1,1,1);
    result.setMilliseconds(value*1000);
    return result;
}
