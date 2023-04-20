<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" omit-xml-declaration="no" indent="yes"/>
    <xsl:strip-space elements="*"/>

    <xsl:template match="node()|@*">
     <xsl:copy>
       <xsl:apply-templates select="node()|@*"/>
     </xsl:copy>
    </xsl:template>
    
    <xsl:template match="ChargeDeviceLocation">
     <xsl:copy>
       <xsl:for-each select="*">
         <xsl:value-of select="text()"/>
         <xsl:if test="position() != last()">
            <xsl:text>,</xsl:text>
         </xsl:if>
       </xsl:for-each>
     </xsl:copy>
    </xsl:template>  

    
</xsl:stylesheet>