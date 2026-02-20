import { utils, writeFile } from 'xlsx';
import { jsPDF } from 'jspdf';
import 'jspdf-autotable';
import { Opportunity } from '../types';

export const exportToCSV = (data: Opportunity[], filename: string) => {
    const headers = ['Opportunity Name', 'Customer', 'Region', 'Practice', 'Deal Value', 'Currency', 'Sales Stage', 'Status'];
    const rows = data.map(o => [
        o.name,
        o.customer,
        o.geo,
        o.practice,
        o.deal_value,
        o.currency,
        o.stage,
        o.workflow_status
    ]);

    const csvContent = [
        headers.join(','),
        ...rows.map(r => r.map(v => `"${v || ''}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `${filename}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
};

export const exportToExcel = (data: Opportunity[], filename: string) => {
    const worksheet = utils.json_to_sheet(data.map(o => ({
        'Opportunity Name': o.name,
        'Customer': o.customer,
        'Region': o.geo,
        'Practice': o.practice,
        'Deal Value': o.deal_value,
        'Currency': o.currency,
        'Sales Stage': o.stage,
        'Status': o.workflow_status
    })));
    const workbook = utils.book_new();
    utils.book_append_sheet(workbook, worksheet, 'Opportunities');
    writeFile(workbook, `${filename}.xlsx`);
};

export const exportToPDF = (data: Opportunity[], filename: string) => {
    const doc = new jsPDF() as any;
    const tableColumn = ['Name', 'Customer', 'Value', 'Stage', 'Status'];
    const tableRows = data.map(o => [
        o.name,
        o.customer,
        `${o.currency || 'USD'} ${o.deal_value?.toLocaleString()}`,
        o.stage,
        o.workflow_status
    ]);

    doc.autoTable({
        head: [tableColumn],
        body: tableRows,
        startY: 20,
        styles: { fontSize: 8 },
        headStyles: { fillStyle: '#b6162d' } // A bit of color
    });
    doc.text('Opportunity Report', 14, 15);
    doc.save(`${filename}.pdf`);
};
