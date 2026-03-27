<script setup lang="ts">
const props = defineProps<{ cron: string }>()

function describeCron(cron: string): string {
  const parts = cron.trim().split(/\s+/)
  if (parts.length !== 5) return cron

  const [minute, hour, dom, month, dow] = parts

  // Every N minutes: */N * * * *
  const everyMinute = minute.match(/^\*\/(\d+)$/)
  if (everyMinute && hour === '*' && dom === '*' && month === '*' && dow === '*') {
    const n = parseInt(everyMinute[1])
    return n === 1 ? 'Every minute' : `Every ${n} minutes`
  }

  // Every N hours: 0 */N * * *
  const everyHour = hour.match(/^\*\/(\d+)$/)
  if (minute === '0' && everyHour && dom === '*' && month === '*' && dow === '*') {
    const n = parseInt(everyHour[1])
    return n === 1 ? 'Every hour' : `Every ${n} hours`
  }

  const fmtTime = (h: string, m: string) => {
    const hh = parseInt(h), mm = parseInt(m)
    const period = hh < 12 ? 'AM' : 'PM'
    const displayH = hh % 12 === 0 ? 12 : hh % 12
    const displayM = mm.toString().padStart(2, '0')
    return `${displayH}:${displayM} ${period}`
  }

  // Every N days at time: M H */N * *
  const everyDay = dom.match(/^\*\/(\d+)$/)
  if (everyDay && month === '*' && dow === '*') {
    const n = parseInt(everyDay[1])
    const timeStr = fmtTime(hour, minute)
    return n === 1 ? `Daily at ${timeStr}` : `Every ${n} days at ${timeStr}`
  }

  // Every N weeks: M H * * 0/N or */N
  const everyWeek = dow.match(/^(?:0\/|\*\/)(\d+)$/)
  if (everyWeek && dom === '*' && month === '*') {
    const n = parseInt(everyWeek[1])
    const timeStr = fmtTime(hour, minute)
    return n === 1 ? `Weekly at ${timeStr}` : `Every ${n} weeks at ${timeStr}`
  }

  // Every N months on the 1st: M H 1 */N *
  const everyMonth = month.match(/^\*\/(\d+)$/)
  if (everyMonth && dom === '1' && dow === '*') {
    const n = parseInt(everyMonth[1])
    const timeStr = fmtTime(hour, minute)
    return n === 1 ? `Monthly on the 1st at ${timeStr}` : `Every ${n} months at ${timeStr}`
  }

  return cron
}
</script>

<template>
  <span>{{ describeCron(props.cron) }}</span>
</template>
