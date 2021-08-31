<?xml version="1.0" encoding="UTF-8"?>
<!--
   This stylesheet converts some of the XML documents belonging to an ASDM dataset version 2
   in order that the resulting files along with the documents which are not transformed
   form an ASDM dataset version 3. 
   
   Attention ! This transformation is specific to the datasets produced at the EVLA and should
   never be applied to datasets produced by ALMA.

   The transformed elements are those whose root elements are :
   
   ASDM
   CalAmpliTable
   CalAtmosphereTable
   CalDelayTable
   CalFocusTable
   ExecBlockTable
   FocusTable
   MainTable
   PolarizationTable
   SBSummaryTable
   ScanTable
   SubscanTable
   WeatherTable

   Author : Rodrigo Avarias & Michel Caillat
   $Id: sdm-v2v3-evla.xsl,v 1.1 2011/08/10 08:17:23 mcaillat Exp $
-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"  version="1.0" >
    
    <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
    
    <xsl:variable name="d-quote">"</xsl:variable>
    
    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()" />
        </xsl:copy>
    </xsl:template>
    
    <!-- Taken from XSLT Cookbook book, only valid for version 1.0 of XSLT standard-->
    <xsl:template name="dup">
        <xsl:param name="input"/>
        <xsl:param name="count" select="2"/>
        <xsl:choose>
            <xsl:when test="not($count) or not($input)"/>
            <xsl:when test="$count = 1">
                <xsl:value-of select="$input"/>
            </xsl:when>
            <xsl:otherwise>
                <!-- If $count is odd append an extra copy of input -->
                <xsl:if test="$count mod 2">
                    <xsl:value-of select="$input"/>
                </xsl:if>
                <!-- Recursively apply template after doubling input and 
                    halving count -->
                <xsl:call-template name="dup">
                    <xsl:with-param name="input" 
                        select="concat($input,$input)"/>
                    <xsl:with-param name="count" 
                        select="floor($count div 2)"/>
                </xsl:call-template>     
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template match="/ASDM|/CalAmpliTable|/CalAtmosphereTable|/CalDelayTable|/CalFocusTable|/ExecBlockTable|/FocusTable|/MainTable|/PolarizationTable|/SBSummaryTable|/ScanTable|/SubscanTable|/WeatherTable">
		<xsl:copy>
       		<xsl:attribute name="schemaVersion">3</xsl:attribute>
       		<xsl:apply-templates select="node()"/>
 	   </xsl:copy>
    </xsl:template>
        
    <xsl:template match="/CalAmpliTable/row/receiverBand" >
        <xsl:copy-of select="."/>
        <xsl:element name="basebandName">
            <xsl:value-of select="'BB_ALL'"/>
        </xsl:element>
    </xsl:template>
    
    <xsl:template match="/CalAtmosphereTable/row/antennaName">
        <xsl:copy-of select="."/>
        <xsl:element name="basebandName">
            <xsl:value-of select="'BB_ALL'"/>
        </xsl:element>
    </xsl:template>
    
    <xsl:template match="/CalDelayTable/row/reducedChiSquared">
        <xsl:copy-of select="."/>
        <xsl:element name="appliedDelay"> <xsl:value-of select="concat('1 ', current()/parent::node()/numReceptor)"/>
            <xsl:call-template name="dup">
                <xsl:with-param name="count"><xsl:value-of select="current()/parent::node()/numReceptor"/></xsl:with-param>
            <xsl:with-param name="input"> 0.0</xsl:with-param>
            </xsl:call-template></xsl:element>
    </xsl:template>
    
    <xsl:template match="/CalFocusTable/row/reducedChiSquared">
        <xsl:copy-of select="."/>
        <xsl:element name="position"> <xsl:value-of select="concat('2 ', current()/parent::node()/numReceptor, ' 3')"/> 
            <xsl:call-template name="dup">
            <xsl:with-param name="count"><xsl:value-of select="current()/parent::node()/numReceptor * 3"/></xsl:with-param>
            <xsl:with-param name="input"> 0.0</xsl:with-param>
            </xsl:call-template></xsl:element>>
    </xsl:template>
    
    <xsl:template match="/ExecBlockTable/row/projectId">
        <xsl:element name="projectUID">
            <xsl:apply-templates select="@* | node()"></xsl:apply-templates>
        </xsl:element>
    </xsl:template>
    
    <xsl:template match="/ExecBlockTable/row/observerName">
        <xsl:copy-of select="."/>
        <xsl:element name="numObservingLog">1</xsl:element>
    </xsl:template>
    
    <xsl:template match="/ExecBlockTable/row/observingLog">
        <xsl:element name="observingLog"><xsl:value-of select="concat('1 1 ', $d-quote, translate(normalize-space(.), $d-quote, ''), $d-quote)"/></xsl:element>
    </xsl:template>
    
    <xsl:template match="/ExecBlockTable/row/sessionReference">
        <xsl:choose>
            <xsl:when test="count(./EntityRef) = 0">
                <xsl:element name="sessionReference">
                    <xsl:element name="EntityRef"> 
                        <xsl:attribute name="entityId"><xsl:value-of select="'uid://A000/X000000/X0'"/></xsl:attribute>
                        <xsl:attribute name="partId"><xsl:value-of select="'X00000000'"/></xsl:attribute>
                        <xsl:attribute name="entityTypeName"><xsl:value-of select="'OUSStatus'"/></xsl:attribute>
                        <xsl:attribute name="documentVersion"><xsl:value-of select="'1.0'"/></xsl:attribute>
                    </xsl:element>
                </xsl:element>
            </xsl:when>
            <xsl:otherwise>
                <xsl:copy-of select="."/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template match="/ExecBlockTable/row/sbSummary"/>
    <xsl:template match="/ExecBlockTable/row/flagRow"/>
    
    <xsl:template match="/FocusTable/row/focusOffset" >
        <xsl:copy-of select="."/>
        <xsl:element name="focusRotationOffset"><xsl:value-of select="'1 2 0.0 0.0'"/></xsl:element>
    </xsl:template>
    
    <xsl:template match="/MainTable/row/dataOid">
        <xsl:element name="dataUID">
            <xsl:apply-templates select="@* | node()"></xsl:apply-templates>
        </xsl:element>
    </xsl:template>
    
    <xsl:template match="/PolarizationTable/row/flagRow" />
    
    <xsl:template match="/SBSummaryTable/row/obsUnitSetId">
        <xsl:element name="obsUnitSetUID">
            <xsl:apply-templates select="@* | node()"></xsl:apply-templates>
        </xsl:element>
    </xsl:template>
    
    <xsl:template match="/ScanTable/row/numSubScan">
        <xsl:element name="numSubscan">
            <xsl:value-of select="."/>
        </xsl:element>
    </xsl:template>
    
    <xsl:template match="/ScanTable/row/flagRow"/>

    <xsl:template match="/SubscanTable/row/numberIntegration">
        <xsl:element name="numIntegration">
            <xsl:value-of select="."/>
        </xsl:element>
    </xsl:template>
    
    <xsl:template match="/SubscanTable/row/numberSubintegration">
        <xsl:element name="numSubintegration">
            <xsl:value-of select="."/>
        </xsl:element>
    </xsl:template>
    
    <xsl:template match="/SubscanTable/row/flagRow"/>   
    
    <xsl:template match="/WeatherTable/row/pressureFlag"/>
    
    <xsl:template match="/WeatherTable/row/relHumidityFlag"/>
    
    <xsl:template match="/WeatherTable/row/temperatureFlag"/>
    
    <xsl:template match="/WeatherTable/row/windDirectionFlag"/>
    
    <xsl:template match="/WeatherTable/row/windSpeedFlag"/>
    
    <xsl:template match="/WeatherTable/row/windMaxFlag"/>
    
    <xsl:template match="/WeatherTable/row/dewPointFlag"/>
    
</xsl:stylesheet>


